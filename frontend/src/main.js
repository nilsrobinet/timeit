import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import './style.css'
import App from './App.vue'

const router = createRouter({
    history: createWebHashHistory(import.meta.env.BASE_URL),
    routes: [
        { path: '/', component: () => import('./pages/TimesheetPage.vue') },
        { path: '/history', component: () => import('./pages/HistoryPage.vue') },
        { path: '/attendance', component: () => import('./pages/AttendancePage.vue') },
        { path: '/settings', component: () => import('./pages/SettingsPage.vue') },
    ]
})

createApp(App).use(router).mount('#app')
