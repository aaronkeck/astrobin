import { HttpClient } from "@angular/common/http";
import { APP_INITIALIZER, NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { FontAwesomeModule } from "@fortawesome/angular-fontawesome";
import { library as fontAwesomeLibrary } from "@fortawesome/fontawesome-svg-core";
import {
  faAsterisk,
  faBarcode,
  faBook,
  faBookmark,
  faChartBar,
  faComments,
  faEdit,
  faEnvelope,
  faEye,
  faGlobe,
  faImage,
  faInbox,
  faInfo,
  faKey,
  faListOl,
  faLock,
  faQuestion,
  faSearch,
  faSignOutAlt,
  faSortAmountDown,
  faStar,
  faTasks,
  faTrophy,
  faUpload,
  faUsers
} from "@fortawesome/free-solid-svg-icons";
import { NgbModule } from "@ng-bootstrap/ng-bootstrap";

import { TranslateLoader, TranslateModule } from '@ngx-translate/core';
import { TranslateHttpLoader } from "@ngx-translate/http-loader";

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { LibraryModule } from "./library/library.module";
import { AppContextService } from "./library/services/app-context.service";
import { SharedModule } from "./library/shared.module";

// AoT requires an exported function for factories
export function HttpLoaderFactory(http: HttpClient) {
  return new TranslateHttpLoader(http, './assets/i18n/', '.json');
}

export function appInitializer(appContext: AppContextService) {
  return () => appContext.load();
}

fontAwesomeLibrary.add(faAsterisk);
fontAwesomeLibrary.add(faBarcode);
fontAwesomeLibrary.add(faBook);
fontAwesomeLibrary.add(faBookmark);
fontAwesomeLibrary.add(faChartBar);
fontAwesomeLibrary.add(faComments);
fontAwesomeLibrary.add(faEdit);
fontAwesomeLibrary.add(faEnvelope);
fontAwesomeLibrary.add(faEye);
fontAwesomeLibrary.add(faGlobe);
fontAwesomeLibrary.add(faImage);
fontAwesomeLibrary.add(faInbox);
fontAwesomeLibrary.add(faInfo);
fontAwesomeLibrary.add(faKey);
fontAwesomeLibrary.add(faListOl);
fontAwesomeLibrary.add(faLock);
fontAwesomeLibrary.add(faQuestion);
fontAwesomeLibrary.add(faSearch);
fontAwesomeLibrary.add(faSignOutAlt);
fontAwesomeLibrary.add(faSortAmountDown);
fontAwesomeLibrary.add(faStar);
fontAwesomeLibrary.add(faTasks);
fontAwesomeLibrary.add(faTrophy);
fontAwesomeLibrary.add(faUpload);
fontAwesomeLibrary.add(faUsers);

@NgModule({
  declarations: [
    AppComponent
  ],
  imports: [
    // Angular
    BrowserModule,

    // Third party
    FontAwesomeModule,
    NgbModule,
    TranslateModule.forRoot({
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      }
    }),

    // App
    AppRoutingModule,
    LibraryModule,
    SharedModule.forRoot()
  ],
  providers: [
    AppContextService,
    {
      provide: APP_INITIALIZER,
      useFactory: appInitializer,
      multi: true,
      deps: [
        AppContextService
      ]
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
