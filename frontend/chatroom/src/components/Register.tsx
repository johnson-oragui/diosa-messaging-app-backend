import { useEffect } from "react";
import { useNavigate, useSearchParams } from 'react-router-dom';

import { useUserData } from "@/context/UserDataContext";
import RegisterForm from '@/components/RegisterForm';


const Register = () => {
  const API_URL: string = import.meta.env.VITE_BACKEND_URL;
  const navigate = useNavigate();
  const { setUserData } = useUserData();

  const [searchParams] = useSearchParams();

  const success = searchParams.get("success");
  const message = searchParams.get("message");
  const token = searchParams.get("token");

  console.log("success: ", success, " message: ", message);

  const handleGoogleRegister = () => {
      window.location.href = `${API_URL}/auth/register/social?provider=google`;
  };
  const handleGithubRegister = () => {
      window.location.href = `${API_URL}/auth/register/social?provider=github`;
  };


  useEffect(() => {
    if (token) {

      fetch(`${API_URL}/users/me`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
        credentials: "include",
      })
        .then((res) => res.json())
        .then((data) => {
          console.log(data.data);
          if (data.status_code == 200) {
            // setUserData
            const userData = { user: data.data.user, profile: data.data.profile };
            setUserData(userData);
            // Navigate to the dashboard and pass userData as state
            navigate(`/dashboard/${user.id}/`);
          } else {
            console.error(data);
          }
        })
        .catch((error) => console.error(error));
    } else if (success == "false") {
      alert(`Registration Failed, Please Try again Later. ${message}`);
    }
  }, []);

  return (
    <div>
      <h1>
        Register
      </h1>

      <button onClick={handleGoogleRegister}>Register with google</button> <br />
      <button onClick={handleGithubRegister}>Register with github</button> <br />

      <RegisterForm />
    </div>
  );
};


export default Register;
