
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DashboardService } from '../../services/dashboard';

@Component({
  selector: 'app-dashboard',
  imports: [CommonModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {

  vulnerabilityCount = 0;
  isLoading = true;
  errorMessage = '';

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadDashboard();
  }

  loadDashboard(): void {
    this.dashboardService.getVulnerabilityCount().subscribe({
      next: (response) => {
        this.vulnerabilityCount = response.count;
        this.isLoading = false;
      },
      error: (error) => {
        this.errorMessage = 'Unable to load vulnerability data.';
        this.isLoading = false;
        console.error('Dashboard error:', error);
      }
    });
  }
}
