import { Component } from '@angular/core';
import { AssociationService } from '../app.service';
import { Association } from './association.model';

@Component({
  selector: 'associations',
  templateUrl: 'association.component.html',
  styleUrls: ['association.component.css']
})
export class AssociationComponent {

  private associations: any[];

  public visible = false;
  private visibleAnimate = false;
  public model: any = {};
  public loading = false;
  public processing = false;
  private error = '';

  constructor(
    public associationService: AssociationService) {

    this.processing = true;

    this.associationService.getAssociations(
    ).subscribe(
      associations => {
        this.associations = associations;
        this.processing = false;
      });
  }

  public show(): void {
    this.visible = true;
    setTimeout(() => this.visibleAnimate = true);
  }

  public hide(): void {
    this.visibleAnimate = false;
    setTimeout(() => this.visible = false, 300);
  }

  public submitAssociation(): void {
    this.loading = true;
    if (this.model.id === undefined) {
      this.associationService.addAssociation(this.model).subscribe(
        result => {
          this.associations.push(result);
          if (result) {
            this.hide();
          } else {
            this.error = 'Username or password is incorrect';
          }
          this.loading = false;
        }
      )
    } else {
      this.associationService.updateAssociation(this.model).subscribe(
        result => {
          for (var i = 0; i < this.associations.length; i++) {
            if (this.associations[i].id == result.id) {
              this.associations[i] = result;
            }
          }
          if (result) {
            this.hide();
          } else {
            this.error = 'Username or password is incorrect';
          }
          this.loading = false;
        }
      )
    }
  }

  public editAssociation(association: Association): void {
    association = Object.assign({}, association);
    this.model = association;
    this.show();
  }

  public deleteAssociation(association: Association): void {
    this.processing = true;
    this.associationService.deleteAssociation(association).subscribe(
      result => {
        for (var i = 0; i < this.associations.length; i++) {
          if (this.associations[i].id == association.id) {
            this.associations.splice(i, 1);
            break;
          }
        }
        this.processing = false;
      }
    )
  }
}
