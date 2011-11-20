import uuid
from datetime import datetime
import glob
import os
import urllib2
import simplejson

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django import forms
from django.utils import translation
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from celery.task import task

from djangoratings.fields import RatingField
from model_utils.managers import InheritanceManager
from timezones.forms import PRETTY_TIMEZONE_CHOICES

from tasks import store_image, solve_image, delete_image
from notifications import push_notification


LICENSE_CHOICES = (
    (0, _("None (All rights reserved)")),
    (1, _("Attribution-NonCommercial-ShareAlike Creative Commons")),
    (2, _("Attribution-NonCommercial Creative Commons")),
    (3, _("Attribution-NonCommercial-NoDerivs Creative Commons")),
    (4, _("Attribution Creative Commons")),
    (5, _("Attribution-ShareAlike Creative Commons")),
    (6, _("Attribution-NoDerivs Creative Commons")),
)


class Gear(models.Model):
    name = models.CharField(_("Name"), max_length=64)

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'astrobin'


class Telescope(Gear):
    focal_length = models.IntegerField(_("Focal length"), null=True, blank=True)
    aperture = models.IntegerField(_("Aperture"), null=True, blank=True)

    class Meta:
        app_label = 'astrobin'


class Mount(Gear):
    pass

    class Meta:
        app_label = 'astrobin'


class Camera(Gear):
    pass

    class Meta:
        app_label = 'astrobin'


class FocalReducer(Gear):
    ratio = models.DecimalField(_("Ratio"), max_digits=3, decimal_places=2, null=True, blank=True)

    class Meta:
        app_label = 'astrobin'


class Software(Gear):
    pass

    class Meta:
        app_label = 'astrobin'


class Filter(Gear):
    pass

    class Meta:
        app_label = 'astrobin'


class Accessory(Gear):
    pass

    class Meta:
        app_label = 'astrobin'


def build_catalog_and_name(obj, name):
    split = name.split(' ')
    if len(split) > 1:
        cat = split[0]
        del(split[0])
        name = ' '.join(split)

        setattr(obj, 'catalog', cat)
    setattr(obj, 'name', name)

class Subject(models.Model):
    # Simbad object id
    oid = models.IntegerField()
    # Right ascension
    ra = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    # Declination
    dec = models.DecimalField(max_digits=8, decimal_places=5, null=True, blank=True)
    # Main object identifier (aka main name)
    mainId = models.CharField(max_length=64, unique=True)
    # Object type
    otype = models.CharField(max_length=16, null=True, blank=True)
    # Morphological type
    mtype = models.CharField(max_length=16, null=True, blank=True)
    # Dimensions along the major and minor axis
    dim_majaxis = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    dim_minaxis = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Catalog name, i.e. fist word of a SIMBAD mainId
    catalog = models.CharField(max_length=64, null=True, blank=True)

    # id of the Subject, excluding the catalog name
    name = models.CharField(max_length=64, default = '')

    # The list of identifier (aka alternative names) is done via
    # a many-to-one relationship in SubjectIdentifier.

    def __unicode__(self):
        return self.mainId

    class Meta:
        app_label = 'astrobin'

    # Note: this function doesn't deal with the alternative names.
    def initFromJSON(self, json):
        for attr in [field.name for field in self._meta.fields]:
            if attr != 'id' and attr in json:
                setattr(self, attr, json[attr])

    def getFromSimbad(self):
        if not self.mainId:
            return
        url = settings.SIMBAD_SEARCH_URL + self.mainId
        f = None
        try:
            f = urllib2.urlopen(url)
        except:
            return;

        json = simplejson.loads(f.read())
        self.initFromJson(json)
        f.close()

    def save(self, *args, **kwargs):
        build_catalog_and_name(self, self.mainId)
        super(Subject, self).save(*args, **kwargs)


class SubjectIdentifier(models.Model):
    identifier = models.CharField(max_length=64, unique=True)
    subject = models.ForeignKey(Subject, related_name='idlist')

    # Catalog name, i.e. fist word of a SIMBAD mainId
    catalog = models.CharField(max_length=64, null=True, blank=True)

    # id of the Subject, excluding the catalog name
    name = models.CharField(max_length=64, default = '')

    class Meta:
        app_label = 'astrobin'

    def __unicode__(self):
        return self.identifier

    def save(self, *args, **kwargs):
        build_catalog_and_name(self, self.identifier)
        super(SubjectIdentifier, self).save(*args, **kwargs)


class Location(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    latitude = models.DecimalField(_("Latitude"), max_digits=7, decimal_places=4, null=True, blank=True)
    longitude = models.DecimalField(_("Longitude"), max_digits=7, decimal_places=4, null=True, blank=True)
    altitude = models.IntegerField(_("Altitude"), null=True, blank=True)
    user_generated = models.BooleanField()

    def __unicode__(self):
        return self.name

    class Meta:
        app_label = 'astrobin'


@task
def image_solved_callback(image, solved, did_use_scale, clean_path, lang):
    if not solved and did_use_scale:
        # Try again!
        solve_image.delay(image, lang, False, callback=image_solved_callback)
        return

    image.is_solved = solved
    if image.__class__.__name__ == 'Image' and image.is_solved:
        # grab objects from list
        list_fn = settings.UPLOADS_DIRECTORY + image.filename + '_resized-list.txt'
        try:
            f = open(list_fn, 'r')

            import simbad
            for line in f:
                if line != '':
                    subjects = simbad.find_subjects(line.partition('/')[0].strip().rstrip('\r\n'))
                    for s in subjects:
                        image.subjects.add(s)
            f.close()
        except:
            image.is_solved = False
            solved = False

    image.save()

    user = None
    img = None
    try:
        user = image.user
        img = image
    except AttributeError:
        # It's a revision
        user = image.image.user
        img = image.image

    translation.activate(lang)
    if solved:
        push_notification([user], 'image_solved',
                          {'object_url':img.get_absolute_url() + '?mod=solved'})
    else:
        push_notification([user], 'image_not_solved',
                          {'object_url':img.get_absolute_url()})

    # Clean up!
    clean_list = glob.glob(clean_path)
    for f in clean_list:
        os.remove(f)


@task
def image_stored_callback(image, stored, solve, lang):
    image.is_stored = stored
    image.save()

    user = None
    img = None
    try:
        user = image.user
        img = image
    except AttributeError:
        # It's a revision
        user = image.image.user
        img = image.image

    translation.activate(lang)
    push_notification([user], 'image_ready', {'object_url':img.get_absolute_url()})

    if solve:
        solve_image.delay(image, lang, callback=image_solved_callback)


class Image(models.Model):
    BINNING_CHOICES = (
        (1, '1x1'),
        (2, '2x2'),
        (3, '3x3'),
        (4, '4x4'),
    )

    title = models.CharField(_("Title"), max_length=128)
    subjects = models.ManyToManyField(Subject, verbose_name=_("Subjects"))
    locations = models.ManyToManyField(Location, null=True, blank=True, verbose_name=_("Locations"))
    description = models.TextField(_("Description"))
    filename = models.CharField(max_length=64, editable=False)
    original_ext = models.CharField(max_length=6, editable=False)
    uploaded = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True, null=True, blank=True)

    focal_length = models.IntegerField(
        null = True,
        blank = True,
        help_text = _("(in mm)"),
        error_messages = {
            'required': _("Insert a focal length if you want to plate-solve."),
        },
        verbose_name = _("Focal length"),
    )

    pixel_size = models.DecimalField(
        null = True,
        blank = True,
        max_digits = 5,
        decimal_places = 2,
        help_text = _("(in &mu;m)"),
        error_messages = {
            'required': _("Insert a pixel size if you want to plate-solve."),
        },
        verbose_name = _("Pixel size"),
    )

    binning = models.IntegerField(
        null      = True,
        blank     = True,
        choices   = BINNING_CHOICES,
        default   = 1,
        help_text = _("This is the smallest of the binning values you used. If you imaged L in 1x1 and RGB in 2x2, put 1x1 here."),
        verbose_name = _("Binning"),
    )

    scaling = models.DecimalField(
        null = True,
        blank = True,
        max_digits = 6,
        decimal_places = 2,
        default = 100,
        help_text = _("If you scaled your image before uploading, enter here the percentage of the new size. E.g. 50 if you made it half the size. Cropping, instead, doesn't matter."),
        verbose_name = _("Scaling"),
    )

    # gear
    imaging_telescopes = models.ManyToManyField(Telescope, null=True, blank=True, related_name='imaging_telescopes', verbose_name=_("Imaging telescopes"))
    guiding_telescopes = models.ManyToManyField(Telescope, null=True, blank=True, related_name='guiding_telescopes', verbose_name=_("Guiding telescopes"))
    mounts = models.ManyToManyField(Mount, null=True, blank=True, verbose_name=_("Mounts"))
    imaging_cameras = models.ManyToManyField(Camera, null=True, blank=True, related_name='imaging_cameras', verbose_name=_("Imaging cameras")) 
    guiding_cameras = models.ManyToManyField(Camera, null=True, blank=True, related_name='guiding_cameras', verbose_name=_("Guiding cameras"))
    focal_reducers = models.ManyToManyField(FocalReducer, null=True, blank=True, verbose_name=_("Focal reducers")) 
    software = models.ManyToManyField(Software, null=True, blank=True, verbose_name=_("Software"))
    filters = models.ManyToManyField(Filter, null=True, blank=True, verbose_name=_("Filters"))
    accessories = models.ManyToManyField(Accessory, null=True, blank=True, verbose_name=_("Accessories"))

    rating = RatingField(range=5)
    user = models.ForeignKey(User)

    is_stored = models.BooleanField(editable=False)
    is_solved = models.BooleanField(editable=False)
    is_wip = models.BooleanField(editable=False, default=False)
    w = models.IntegerField(editable=False, default=0)
    h = models.IntegerField(editable=False, default=0)
    animated = models.BooleanField(editable=False, default=False)

    license = models.IntegerField(
        choices = LICENSE_CHOICES,
        default = 0,
        verbose_name = _("License"),
    )

    is_final = models.BooleanField(
        editable = False,
        default = True
    )

    class Meta:
        app_label = 'astrobin'
        ordering = ('-uploaded', '-id')
        
    def __unicode__(self):
        return self.title if self.title is not None else _("(no title)")

    def save(self, *args, **kwargs):
        super(Image, self).save(*args, **kwargs)

        # Find requests and mark as fulfilled
        try:
            req = ImageRequest.objects.filter(
                image = self.id,
                type = 'INFO',
                fulfilled = False)
            for r in req:
                r.fulfilled = True
                r.save()
                push_notification(
                    [r.from_user], 'request_fulfilled',
                    {'object': self,
                     'object_url': settings.ASTROBIN_BASE_URL + self.get_absolute_url(),
                     'originator': r.to_user,
                     'originaror_url': r.to_user.get_absolute_url()})
        except:
            pass

    def process(self, solve=False):
        store_image.delay(self, solve=solve, lang=translation.get_language(), callback=image_stored_callback)

    def solve(self):
        solve_image.delay(self, lang=translation.get_language(), callback=image_solved_callback)

    def delete(self, *args, **kwargs):
        delete_image.delay(self.filename, self.original_ext) 

        # Delete references
        for r in ImageRequest.objects.filter(image=self):
            r.delete()

        # Delete revisions
        for r in ImageRevision.objects.filter(image=self):
            r.delete()

        super(Image, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return '/%i' % self.id


class ImageRevision(models.Model):
    image = models.ForeignKey(Image)
    filename = models.CharField(max_length=64, editable=False)
    original_ext = models.CharField(max_length=6, editable=False)
    uploaded = models.DateTimeField(editable=False, auto_now_add=True)

    w = models.IntegerField(editable=False, default=0)
    h = models.IntegerField(editable=False, default=0)

    is_stored = models.BooleanField(editable=False)
    is_solved = models.BooleanField(editable=False)

    is_final = models.BooleanField(
        editable = False,
        default = False
    )

    class Meta:
        app_label = 'astrobin'
        ordering = ('uploaded', '-id')
        
    def __unicode__(self):
        return 'Revision for %s' % self.image.title

    def process(self):
        store_image.delay(self, solve=False, lang=translation.get_language(), callback=image_stored_callback)

    def delete(self, *args, **kwargs):
        delete_image.delay(self.filename, self.original_ext) 
        super(ImageRevision, self).delete(*args, **kwargs)

    def get_absolute_url(self):
        return '/%i?r=%i' % (self.image.id, self.id)
 

class Acquisition(models.Model):
    date = models.DateField(_("Date"), null=True, blank=True, help_text=_("Please use the following format: yyyy-mm-dd"))
    image = models.ForeignKey(Image, verbose_name=_("Image"))

    class Meta:
        app_label = 'astrobin'

    def __unicode__(self):
        return self.image.title


class DeepSky_Acquisition(Acquisition):
    BINNING_CHOICES = (
        (1, '1x1'),
        (2, '2x2'),
        (3, '3x3'),
        (4, '4x4'),
    )

    is_synthetic = models.BooleanField(
        _("Synthetic channel"))

    filter = models.ForeignKey(
        Filter,
        null=True, blank=True,
        verbose_name=_("Filter"))

    binning = models.IntegerField(
        null=True, blank=True,
        choices=BINNING_CHOICES,
        default=1,
        verbose_name=_("Binning"))

    number = models.IntegerField(
        _("Number"),
        null=True, blank=True,
        help_text=_("The number of sub-frames."))

    duration = models.IntegerField(
        _("Duration"),
        null=True, blank=True,
        help_text=_("Duration of each sub-frame, in seconds."))

    iso = models.IntegerField(
        _("ISO"),
        null=True, blank=True)

    gain = models.DecimalField(
        _("Gain"),
        null=True, blank=True,
        max_digits=5, decimal_places=2)

    sensor_cooling = models.IntegerField(
        _("Sensor cooling"),
        null=True, blank=True,
        help_text=_("The temperature of the chip. E.g.: -20."))

    darks = models.IntegerField(
        _("Darks"),
        null=True, blank=True,
        help_text=_("The number of dark frames."))

    flats = models.IntegerField(
        _("Flats"),
        null=True, blank=True,
        help_text=_("The number of flat frames."))

    flat_darks = models.IntegerField(
        _("Flat darks"),
        null=True, blank=True,
        help_text=_("The number of dark flat frames."))

    bias = models.IntegerField(
        _("Bias"),
        null=True, blank=True,
        help_text=_("The number of bias/offset frames."))

    mean_sqm = models.DecimalField(
        _("Mean SQM"),
        null=True, blank=True,
        max_digits=5, decimal_places=2)

    mean_fwhm = models.DecimalField(
        _("Mean FWHM"),
        null=True, blank=True,
        max_digits=5, decimal_places=2)

    advanced = models.BooleanField(
        editable=False,
        default=False)

    saved_on = models.DateTimeField(
        editable=False,
        auto_now=True,
        null=True)

    class Meta:
        app_label = 'astrobin'
        ordering = ['-saved_on', 'filter']


class SolarSystem_Acquisition(Acquisition):
    frames = models.IntegerField(_("Frames"), null=True, blank=True)
    fps = models.DecimalField(_("FPS"), max_digits=12, decimal_places=5, null=True, blank=True)
    focal_length = models.IntegerField(_("Focal length"), null=True, blank=True)
    cmi = models.DecimalField(_("CMI"), null=True, blank=True, max_digits=5, decimal_places=2)
    cmii = models.DecimalField(_("CMII"), null=True, blank=True, max_digits=5, decimal_places=2)
    cmiii = models.DecimalField(_("CMIII"), null=True, blank=True, max_digits=5, decimal_places=2)
    seeing = models.IntegerField(_("Seeing"), null=True, blank=True)
    transparency = models.IntegerField(_("Transparency"), null=True, blank=True)
    time = models.CharField(_("Time"), null=True, blank=True, max_length=5)

    class Meta:
        app_label = 'astrobin'


class ABPOD(models.Model):
    image = models.ForeignKey(Image, unique=True, verbose_name=_("Image"))
    date = models.DateTimeField(_("Date"))

    def __unicode__(self):
        return self.image.title

    class Meta:
        app_label = 'astrobin'


class Request(models.Model):
    from_user = models.ForeignKey(User, editable=False, related_name='requester')
    to_user   = models.ForeignKey(User, editable=False, related_name='requestee')
    fulfilled = models.BooleanField()
    message   = models.CharField(max_length=255)
    created   = models.DateTimeField(auto_now_add=True)

    objects   = InheritanceManager()

    def __unicode__(self):
        return '%s %s: %s' % (_('Request from'), self.from_user.username, self.message)

    class Meta:
        app_label = 'astrobin'
        ordering = ['-created']

    def get_absolute_url():
        return '/requests/detail/' + self.id + '/'


class ImageRequest(Request):
    TYPE_CHOICES = (
        ('INFO',     _('Additional information')),
        ('FITS',     _('TIFF/FITS')),
        ('HIRES',    _('Higher resolution')),
    )

    image = models.ForeignKey(Image, editable=False)
    type  = models.CharField(max_length=8, choices=TYPE_CHOICES)


class LocationRequest(Request):
    location = models.ForeignKey(Location, editable=False)


class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True, editable=False)

    # Basic Information
    locations = models.ManyToManyField(Location, null=True, blank=True, verbose_name=_("Locations"))
    website = models.CharField(_("Website"), max_length=128, null=True, blank=True)
    job = models.CharField(_("Job"), max_length=128, null=True, blank=True)
    hobbies = models.CharField(_("Hobbies"), max_length=128, null=True, blank=True)
    language = models.CharField(_("Language"), max_length=8, null=True, blank=True, editable=False)
    timezone = models.CharField(
        max_length=255,
        choices=PRETTY_TIMEZONE_CHOICES,
        blank=True, null=True,
        verbose_name=_("Timezone"),
        help_text=_("By selecting this, you will see all the dates on AstroBin in your timezone."))

    # Avatar
    avatar = models.CharField(max_length=64, editable=False, null=True, blank=True)

    # Gear
    telescopes = models.ManyToManyField(Telescope, null=True, blank=True, verbose_name=_("Telescopes"))
    mounts = models.ManyToManyField(Mount, null=True, blank=True, verbose_name=_("Mounts"))
    cameras = models.ManyToManyField(Camera, null=True, blank=True, verbose_name=_("Cameras"))
    focal_reducers = models.ManyToManyField(FocalReducer, null=True, blank=True, verbose_name=_("Focal reducers"))
    software = models.ManyToManyField(Software, null=True, blank=True, verbose_name=_("Software"))
    filters = models.ManyToManyField(Filter, null=True, blank=True, verbose_name=_("Filters"))
    accessories = models.ManyToManyField(Accessory, null=True, blank=True, verbose_name=_("Accessories"))

    follows = models.ManyToManyField('self', null=True, blank=True, related_name='followers', symmetrical=False)

    default_license = models.IntegerField(
        choices = LICENSE_CHOICES,
        default = 0,
        verbose_name = _("Default license"),
        help_text = _(
            "The license you select here is automatically applied to "
            "all your new images."
        ),
    )

    def __unicode__(self):
        return "%s' profile" % self.user.username

    def get_absolute_url(self):
        return '/users/%s' % self.user.username

    class Meta:
        app_label = 'astrobin'


def create_user_profile(sender, instance, created, **kwargs):  
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)

