import {
  Component,
  OnInit
} from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { Observable } from 'rxjs';

@Component({
  selector: 'foo',
  styles: [`
  `],
  template: `
    <h1>Foo!!!</h1>
    <div>
      For hot module reloading run
      <pre>npm run start:hmr</pre>
    </div>
    <div>
      <h3>
        patrick@AngularClass.com
      </h3>
    </div>
    <pre>this.localState = {{ localState | json }}</pre>
  `
})
export class FooComponent implements OnInit {

  public localState: any;
  constructor(
    public activatedRoute: ActivatedRoute,
    public router: Router
  ) {

    console.log('URL: ');
    console.log(this.router.url);
  }

  public ngOnInit() {

    this.activatedRoute
      .data
      .subscribe((data: any) => {
        // your resolved data from route
        this.localState = data.yourData;
      });

    console.log('hello `About` component');

    this.asyncDataWithWebpack();
  }
  private asyncDataWithWebpack() {
    // you can also async load mock data with 'es6-promise-loader'
    // you would do this if you don't want the mock-data bundled
    // remember that 'es6-promise-loader' is a promise
    setTimeout(() => {

      System.import('../../assets/mock-data/mock-data.json')
        .then((json) => {
          console.log('async mockData', json);
          this.localState = json;
        });

    });
  }

}
