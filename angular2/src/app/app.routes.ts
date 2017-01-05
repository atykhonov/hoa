import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home';
import { AboutComponent } from './about';
import { NoContentComponent } from './no-content';
import { FooComponent } from './foo';
import { LoginComponent } from './login';
import { AssociationComponent } from './association';
import { AuthGuard } from './guard';

import { DataResolver } from './app.resolver';

export const ROUTES: Routes = [
  { path: '',      component: HomeComponent },
  { path: 'home',  component: HomeComponent },
  { path: 'about', component: AboutComponent },
  { path: 'foo', component: FooComponent, canActivate: [AuthGuard] },
  { path: 'associations', component: AssociationComponent, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent },
  { path: 'detail', loadChildren: './+detail/index#DetailModule'},
  { path: '**',    component: NoContentComponent },
];
