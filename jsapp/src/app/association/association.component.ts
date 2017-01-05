import {
  Component,
  OnInit,
  ViewEncapsulation
} from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AssociationService } from '../app.service';
import { GridOptions } from 'ag-grid/main';
import { AgGridNg2 } from 'ag-grid-ng2/main';

@Component({
  selector: 'grid',
  templateUrl: 'association.component.html',
  styleUrls: [
  ]
})
export class AssociationComponent {

  // public localState: any;

  private gridOptions: GridOptions;
  // private showGrid: boolean;
  // private rowCount: string;
  private columnDefs: any[];
  private rowData: any[];
  private associations: any[];

  constructor(
    public associationService: AssociationService) {
    // this.gridOptions = <GridOptions>{};
    // this.createColumnDefs();
    // this.showGrid = true; ``
    // this.listData = [];
    // test
    // this.gridOptions = <GridOptions>{};
    // this.createRowData();
    // this.createColumnDefs();
    // this.showGrid = true;
    console.log("in Grid constructor...");

    this.columnDefs = [{
      headerName: "ID",
      field: "id",
      sortingOrder: ["asc", "desc"],
      editable: false,
      width: 100
    }, {
      headerName: "Name",
      field: "name",
      sortingOrder: ["asc", "desc"],
      editable: false,
      hide: false
    }];

    this.associationService.getAssociations()
      .subscribe(associations => {
        var rowData: any[] = [];
        for (var i = 0; i < associations.length; i++) {
          rowData.push({
            id: associations[i].id,
            name: associations[i].name
          });
        }
        this.rowData = rowData;
        this.associations = associations;
      });

    this.gridOptions = {
      enableSorting: true,
      rowData: this.rowData,
      columnDefs: this.columnDefs,
      onGridReady: () => {
        this.gridOptions.api.sizeColumnsToFit();
        console.log(this.gridOptions.api);
      }
    }
  }
}
