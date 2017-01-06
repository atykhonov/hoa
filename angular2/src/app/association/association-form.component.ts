import { Component } from '@angular/core';
import { Association } from './association.model';

@Component({
  selector: 'association-form',
  templateUrl: 'association-form.component.html'
})
export class AssociationFormComponent {
  powers = ['Really Smart', 'Super Flexible',
    'Super Hot', 'Weather Changer'];
  // model = new Association(18, 'Dr IQ', this.powers[0], 'Chuck Overstreet');
  submitted = false;
  onSubmit() { this.submitted = true; }
  // TODO: Remove this when we're done
  // get diagnostic() { return JSON.stringify(this.model); }
}
