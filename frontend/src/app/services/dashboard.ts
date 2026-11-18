
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Auth } from './auth';

@Injectable({
  providedIn: 'root'
})
export class DashboardService {

  private apiUrl = '/api/v1/vulnerabilities';

  constructor(
    private http: HttpClient,
    private auth: Auth
  ) {}

  getVulnerabilityCount(): Observable<any> {

    const headers = new HttpHeaders({
      Authorization: this.auth.getBasicAuthHeader()
    });

    return this.http.get(
      `${this.apiUrl}/count`,
      { headers }
    );
  }
}
