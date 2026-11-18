
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class Auth {
  private apiUrl = '/api/v1/auth';

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<AuthResponse> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    return this.http.post<AuthResponse>(
      `${this.apiUrl}/login`,
      formData
    ).pipe(
      tap(response => {
        localStorage.setItem('access_token', response.access_token);
      })
    );
  }

  register(username: string, password: string): Observable<any> {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    return this.http.post(
      `${this.apiUrl}/register`,
      formData
    );
  }

  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  logout(): void {
    localStorage.removeItem('access_token');
  }
}
