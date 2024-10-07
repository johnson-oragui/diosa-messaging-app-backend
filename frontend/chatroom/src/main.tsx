import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import * as ReactRouter from 'react-router-dom';

import App from './App.tsx';
import ErrorPage from '@/components/Error-page';
import Register from "@/components/Register";
import Login from "@/components/Login";
import Dashboard from "@/components/Dashboard";
import Profile from "@/components/Profile";
import { UserDataProvider } from "@/context/UserDataContext";

import './index.css';

const router = ReactRouter.createBrowserRouter([
  {
    path: "/",
    element: <App />,
    errorElement: <ErrorPage />,
    children: [
      {
        path: "register/",
        element: <Register />
      },
      {
        path: "login/",
        element: <Login />
      },
      {
        path: "dashboard/:user_id",
        element: <Dashboard />
      },
      {
        path: "profile/:user_id",
        element: <Profile />
      },
      
    ]
  },
]);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <UserDataProvider>
      <ReactRouter.RouterProvider router={router}/>
    </UserDataProvider>
  </StrictMode>,
)
