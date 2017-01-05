import {
  Component,
  OnInit
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AssociationService } from '../app.service';

@Component({
  selector: 'associations',
  templateUrl: 'association.component.html',
  styleUrls: [
  ]
})
export class AssociationComponent {

  private associations: any[];

  constructor(
    public associationService: AssociationService) {

    this.associationService.getAssociations()
      .subscribe(associations => {
        this.associations = associations;
      });
  }
}
