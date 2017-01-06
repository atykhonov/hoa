import {
  Component,
  OnInit
} from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'navbar',
  templateUrl: 'navbar.component.html',
  styleUrls: [
  ]
})
export class NavbarComponent {

  public url = '';

  constructor(public router: Router) {
    this.url = this.router.url;
  }

  isAssociationsActive(): boolean {
    return this.router.url == '/associations';
  }

  isFooActive(): boolean {
    return this.router.url == '/foo';
  }

  isLoginActive(): boolean {
    return this.router.url == '/login';
  }
}
