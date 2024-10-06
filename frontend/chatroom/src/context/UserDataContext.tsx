import { createContext, useContext, useState, useEffect } from "react";

/// Define the shape of your user data
interface UserData {
    user: User;
    profile: Profile;
}

interface User {
    id: string;
    email: string;
    username: string;
    first_name: string;
    last_name: string;
    status: string;
    created_at: datetime;
    updated_at: datetime;
};

interface Profile {
    id: string;
    gender: string;
    recovery_email?: string;
    bio?: string;
    profession?: string;
    avatar_url?: string;
    facebook_link?: string;
    x_link?: string;
    instagram_link?: string;
    created_at: datetime;
    updated_at: datetime;
}

interface UserDataContextType {
    UserData: UserData | null;
    setUserData: (UserData: UserData | null) => void;
    isLoading: boolean;
}

// Create the User Context
const UserDataContext = createContext<UserDataContextType | undefined>(undefined);

// Custom hook to use UserDataContext easily
export const useUserData = () => {
    const context = useContext(UserDataContext);
    if (!context) {
        throw new Error("useUserData must be used within a userDataProvider");
    }

    return context;
};

// UserDataProvider to wrap the app and manage global state
export const UserDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [userData, setUserData] = useState<UserData | null>(null);
    const [isLoading, setIsLoading] = useState(true); 

    // On initialization, check if there's user data in local storage
    useEffect(() => {
        // Load user data from localStorage when the app initializes
      const storedUserData = localStorage.getItem("userData");
      if (storedUserData) {
        setUserData(JSON.parse(storedUserData));
      }
      setIsLoading(false);  // Loading is done after checking localStorage
    
    }, [])
  
    // Store user data in localStorage whenever it changes
    useEffect(() => {
        // Update local storage whenever userData changes
        if (userData) {
            localStorage.setItem("userData", JSON.stringify(userData));
        }
    }, [userData]);

    return (
        <UserDataContext.Provider value={{ userData, setUserData, isLoading }}>
            {children}
        </UserDataContext.Provider>
    );

};
