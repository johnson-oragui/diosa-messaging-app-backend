import React, { useEffect, useState } from "react";

const LoginForm = () => {
    const [input, setInput] = useState({
        username: "",
        password: "",
    });

    const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        console.log("submitted login form");
    };

    const handleInput = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setInput((prevInput) => ({
            ...prevInput,
            [name]: value,
        }));
        console.log(value);
    };

    useEffect(() => {
 
    }, [])
    
    return (
        <div className="bg-gray-100 dark:bg-gray-900">
            <div className="w-full max-w-3xl mx-auto p-8">
                <div className="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-md border dark:border-gray-700">
                    <h1 className="text-2xl font-bold text-gray-800 dark:text-white mb-4">Login</h1>
    
                    <form onSubmit={handleSubmit}>
                        <div className="mb-6">
                            <h2 className="text-xl font-semibold text-gray-700 dark:text-white mb-2">Login</h2>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label htmlFor="username" className="block text-gray-700 dark:text-white mb-1">
                                        Username
                                    </label>
                                    <input
                                        id="username"
                                        name="username"
                                        onChange={handleInput}
                                        value={input.username}
                                        className="w-full rounded-lg border py-2 px-3 dark:bg-gray-700 dark:text-white dark:border-none" />
                                </div>

                                <div>
                                    <label htmlFor="password" className="block text-gray-700 dark:text-white mb-1">
                                        Password
                                    </label>
                                    <input
                                        type="password"
                                        id="password"
                                        name="password"
                                        onChange={handleInput}
                                        value={input.password}
                                        className="w-full rounded-lg border py-2 px-3 dark:bg-gray-700 dark:text-white dark:border-none" />
                                </div>
                            </div>
                        </div>
                        <div className="mt-8 flex justify-end">
                            <button type="submit" className="bg-teal-500 text-white px-4 py-2 rounded-lg hover:bg-teal-700 dark:bg-teal-600 dark:text-white dark:hover:bg-teal-900">
                                Login
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    
);
};

export default LoginForm;
