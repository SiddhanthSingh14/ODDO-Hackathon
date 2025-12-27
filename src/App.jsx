import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppProvider } from './context/AppContext';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import KanbanBoard from './pages/KanbanBoard';
import CalendarView from './pages/CalendarView';
import Reports from './pages/Reports';
import EquipmentList from './pages/EquipmentList';
import './App.css';

function App() {
  return (
    <AppProvider>
      <Router>
        <div className="app-container">
          <Sidebar />
          <div className="main-content">
            <Header />
            <div className="page-content">
              <Routes>
                <Route path="/" element={<Navigate to="/kanban" replace />} />
                <Route path="/kanban" element={<KanbanBoard />} />
                <Route path="/calendar" element={<CalendarView />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/equipment" element={<EquipmentList />} />
              </Routes>
            </div>
          </div>
        </div>
      </Router>
    </AppProvider>
  );
}

export default App;
