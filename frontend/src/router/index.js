import { createRouter, createWebHistory } from 'vue-router';
import MaintenanceRateManager from '../components/MaintenanceRateManager.vue';
import ServiceLevel from '../views/ServiceLevel.vue';
import BackendManagement from '../views/BackendManagement.vue';
import GPUPriceManager from '../views/GPUPriceManager.vue';

const routes = [
  {
    path: '/',
    redirect: '/backend-management/rate-management'
  },
  {
    path: '/backend-management',
    name: 'BackendManagement',
    component: BackendManagement,
    children: [
      {
        path: 'rate-management',
        name: 'RateManagement',
        component: MaintenanceRateManager
      },
      {
        path: 'service-level',
        name: 'ServiceLevel',
        component: ServiceLevel
      }
      ,{
        path: 'gpu-price',
        name: 'GPUPrice',
        component: GPUPriceManager
      }
    ]
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router; 