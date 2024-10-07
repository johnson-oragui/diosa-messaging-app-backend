import React from "react";
import { Link } from "react-router-dom";

import { useUserData } from "@/context/UserDataContext";
import Logout from "@/components/Logout";

const Footer = () => {
    const year = new Date().getCurrentYear();

    const userData = useUserData();
    return (
        <>
            <footer class="flex flex-col space-y-10 justify-center m-10 pt-96">

            <nav className="flex justify-center flex-wrap gap-6 text-gray-500 font-medium">
                    <a className="hover:text-gray-300" href="/">Home</a>
                    {
                        !userData.user ? (
                            <a className="hover:text-gray-300" ><Link to={'login'}>Login</Link></a>
                        ) : (
                            null
                        )
                    }
                    {
                        userData.user ? (
                            <Logout/>
                        ) : (
                            null
                        )
                    }
                    {
                        !userData.user ? (
                            <a className="hover:text-gray-300"><Link to={'register'}>Register</Link></a>
                        ) : (
                            null
                        )
                    }
                    {
                        userData.user ? (
                            <a className="hover:text-gray-300" ><Link to={`/dashboard/${userData.user.id}`}>Dashboard</Link></a>
                        ) : (
                            null
                        )
                    }
                    {
                        userData.user ? (
                            <a className="hover:text-gray-300" href="/inbox">Inbox</a>
                        ) : (
                            null
                        )
                    }
                    <a className="hover:text-gray-300" href="#">Contact</a>
            </nav>

                <div class="flex justify-center space-x-5">
                    <a href="https://facebook.com" target="_blank" rel="noopener noreferrer">
                        <img src="https://img.icons8.com/fluent/30/000000/facebook-new.png" />
                    </a>
                    <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer">
                        <img src="https://img.icons8.com/fluent/30/000000/linkedin-2.png" />
                    </a>
                    <a href="https://instagram.com" target="_blank" rel="noopener noreferrer">
                        <img src="https://img.icons8.com/fluent/30/000000/instagram-new.png" />
                    </a>
                    <a href="https://messenger.com" target="_blank" rel="noopener noreferrer">
                        <img src="https://img.icons8.com/fluent/30/000000/facebook-messenger--v2.png" />
                    </a>
                    <a href="https://twitter.com" target="_blank" rel="noopener noreferrer">
                        <img src="https://img.icons8.com/fluent/30/000000/twitter.png" />
                    </a>
                </div>
                <p class="text-center text-gray-700 font-medium">&copy; {year} Company Ltd. All rights reservered.</p>
                </footer>
        </>
    );
};

export default Footer;
