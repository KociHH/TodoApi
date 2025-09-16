import { securedApiCall } from "../utils/security.js"

document.addEventListener("DOMContentLoaded", async () => {
    const form = document.getElementById("create_task-form") as HTMLFormElement;

    form.addEventListener("submit", async (e) => {
        const title = (document.getElementById("title") as HTMLInputElement).value
        const description = (document.getElementById("description") as HTMLInputElement).value

        const response = await securedApiCall("/todo/create", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                title,
                description
            })
        });

        if (response && response.ok) {
            const data = await response.json();

            if (data.success) {
                window.location.href = "/todo/tasks";
                return;

            } else {
                throw Error
            }

        } else {
            console.error("Ошибка возврат данных /todo/create");
            return; 
        }
    })
})