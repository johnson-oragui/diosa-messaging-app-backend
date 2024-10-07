import { Link } from "react-router-dom";
import Logout from "@/components/Logout";
import { useUserData } from '@/context/UserDataContext';



export default function Navbar() {
    const userData = useUserData();
    return (
        <div className="flex justify-center mb-72">
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
            
        </div>
          
    );
};
