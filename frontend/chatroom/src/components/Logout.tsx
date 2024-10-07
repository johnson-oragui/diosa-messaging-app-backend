import React from 'react';
import { useNavigate } from 'react-router-dom';

import { useUserData } from '@/context/UserDataContext';


export default function Logout(): React.FC {
  const { setUserData } = useUserData();
  const navigate = useNavigate();

  const handleLogout = () => {
    
    fetch("/api/v1/auth/logout", {
        method: "POST",
        credentials: "include"
    })
        .then((response) => {
            if (response.ok) {
                setUserData(null); // Clear user state
                console.log("Logged out successfully");
            }
        })
        .catch((error) => {
            console.error("Logout Failed: ", error)
        });
    navigate('/login'); // Redirect to login page
  };

  return (
    <button onClick={handleLogout}>Log Out</button>
  );
};
