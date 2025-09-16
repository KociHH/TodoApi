import { ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY } from "./utils/security.js";

document.addEventListener("DOMContentLoaded", () => {
    
    const access_token = localStorage.getItem(ACCESS_TOKEN_KEY)

    if (access_token) {
        window.location.href = "/todo/tasks";
        return;
    }

    const form = document.getElementById("login-form") as HTMLElement;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const name = (document.getElementById("name") as HTMLInputElement).value
        const password = (document.getElementById("password") as HTMLInputElement).value

        const response = await fetch("/login", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name,
                password,
            })
        })

        if (response && response.ok) {
            const data = await response.json();

            if (data.success) {
                localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token)
                localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token)

                window.location.href = "/todo/tasks";
                return;

            } else {
                alert(data.message)
            }

        } else {
            console.error("Ошибка возврат данных /login");
            return;
        }
    })
})