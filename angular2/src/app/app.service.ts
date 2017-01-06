import { Injectable } from '@angular/core';
import { Http, Headers, RequestOptions, Response } from '@angular/http';
import { Observable } from 'rxjs';
import { Association } from './association/association.model';
import 'rxjs/add/operator/map'

import { User } from './user';

export type InternalStateType = {
  [key: string]: any
};

@Injectable()
export class AppState {

  public _state: InternalStateType = { };

  // already return a clone of the current state
  public get state() {
    return this._state = this._clone(this._state);
  }
  // never allow mutation
  public set state(value) {
    throw new Error('do not mutate the `.state` directly');
  }

  public get(prop?: any) {
    // use our state getter for the clone
    const state = this.state;
    return state.hasOwnProperty(prop) ? state[prop] : state;
  }

  public set(prop: string, value: any) {
    // internally mutate our state
    return this._state[prop] = value;
  }

  private _clone(object: InternalStateType) {
    // simple object clone
    return JSON.parse(JSON.stringify( object ));
  }
}

@Injectable()
export class AuthenticationService {
  public token: string;

  constructor(private http: Http) {
    // set token if saved in local storage
    var currentUser = JSON.parse(localStorage.getItem('currentUser'));
    this.token = currentUser && currentUser.token;
  }

  login(email: string, password: string): Observable<boolean> {
    let headers = new Headers({ 'Content-Type': 'application/json' });
    let options = new RequestOptions({ headers: headers });
    return this.http.post('http://localhost:8000/api-token-auth/', JSON.stringify({ email: email, password: password }), options)
      .map((response: Response) => {
        // login successful if there's a jwt token in the response
        let token = response.json() && response.json().token;
        if (token) {
          // set token property
          this.token = token;

          // store username and jwt token in local storage to keep user logged in between page refreshes
          localStorage.setItem('currentUser', JSON.stringify({ email: email, token: token }));

          // return true to indicate successful login
          return true;
        } else {
          // return false to indicate failed login
          return false;
        }
      });
  }

  logout(): void {
    // clear token remove user from local storage to log user out
    this.token = null;
    localStorage.removeItem('currentUser');
  }

  private getHeaders(){
    let headers = new Headers();
    headers.append('Accept', 'application/json');
    headers.append('Content-Type', 'application/json')
    return headers;
  }
}

@Injectable()
export class UserService {
    constructor(
        private http: Http,
        private authenticationService: AuthenticationService) {
    }

    getUsers(): Observable<User[]> {
      let headers = new Headers({
        'Content-Type': 'application/json'
      });
      let options = new RequestOptions({ headers: headers });

      return this.http.get('http://localhost:8000/api/v1/users', options)
        .map((response: Response) => response.json());
    }
}

@Injectable()
export class AssociationService {

  private associationsUrl = 'http://localhost:8000/api/v1/cooperatives/';

  private associationUrl = 'http://localhost:8000/api/v1/cooperatives/';

  constructor(
    private http: Http,
    private authenticationService: AuthenticationService) {
  }

  getAssociations(): Observable<Association[]> {
    return this.http.get(
      this.associationsUrl,
      this.getRequestOptions(),
    ).map((response: Response) => {
      let body = response.json();
      return body || { };
    });
  }

  addAssociation(association: Association): Observable<Association> {
    return this.http.post(
      this.associationsUrl,
      JSON.stringify(association),
      this.getRequestOptions()
    ).map((response: Response) => {
      let body = response.json();
      return body || {};
    })
  }

  updateAssociation(association: Association): Observable<Association> {
    let url = `${this.associationUrl}${association.id}/`;
    return this.http.put(
      url,
      JSON.stringify(association),
      this.getRequestOptions()
    ).map((response: Response) => {
      let body = response.json();
      return body || {};
    })
  }

  deleteAssociation(association: Association): Observable<Association> {
    let url = `${this.associationUrl}${association.id}/`;
    return this.http.delete(
      url,
      this.getRequestOptions()
    ).map((response: Response) => {
      let body = response.json();
      console.log(body);
      return body || {};
    })
  }

  private getRequestOptions(): RequestOptions {
    let headers = new Headers({
      'Authorization': ' JWT ' + this.authenticationService.token,
      'Content-Type': 'application/json'
    });
    return new RequestOptions({ headers: headers });    
  }
}
