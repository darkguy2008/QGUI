import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-welcome',
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss']
})
export class WelcomeComponent implements OnInit {

  wizardStep: number = 1;

  constructor() { }
  ngOnInit(): void { }

  next() { this.wizardStep++; }

}
