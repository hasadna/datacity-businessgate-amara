import { Component, Input, OnInit } from '@angular/core';
import { timer } from 'rxjs';

@Component({
  selector: 'app-copy-link',
  templateUrl: './copy-link.component.html',
  styleUrls: ['./copy-link.component.less']
})
export class CopyLinkComponent implements OnInit {
  @Input() link = window.location.href;;

  clipboardSupported = false;
  copied = false;

  constructor() {
    try {
      this.clipboardSupported = document.queryCommandSupported && document.queryCommandSupported('copy');
    } catch (e) {
      console.log('Failed to check if copy clipboard is available');
    }
  }

  clipboardCopy(): string {
    if (!this.clipboardSupported) {
      return;
    }
    const text = this.link;
    const txt = document.createElement('textarea');
    txt.textContent = text;
    txt.classList.add('visually-hidden');
    document.body.appendChild(txt);
    txt.select();
    try {
      document.execCommand('copy');
      this.copied = true;
      timer(3000).subscribe(() => {
        this.copied = false;
      });
    } catch (ex) {
      console.log('FAILED TO COPY', ex);
    } finally {
      document.body.removeChild(txt);
    }
  }

  ngOnInit(): void {
  }
}
