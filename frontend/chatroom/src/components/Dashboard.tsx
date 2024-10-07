import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

import { useUserData } from '@/context/UserDataContext';

export default function Dashboard(): React.FC {
    const { userData, isLoading } = useUserData();
    const navigate = useNavigate();

    useEffect(() => {
        // Simulate loading userData
        if (!isLoading && !userData) {
            // If userData is not available, redirect to login
            navigate("/login");
        }
    }, [isLoading, userData, navigate]);
    
    if (isLoading) {
        // Render a loading indicator while waiting for userData
        return <p>Loading...</p>;
    }
    
    return (
        <>
        <div>
            <h1 className="">
                Dashboard
            </h1>
            {
                userData ? (
                    <h1>
                        Welcome, {userData.user.first_name}
                    </h1>
                ) : (
                    <p>Please log in to view your dashboard.</p>
                )
            }
        </div>
        </>
    );
};
