import { checkUpdateTokens, securedApiCall } from "../utils/security.js";

class ChangeTask {
    public oldTitle: string | null = null
    public oldDescription: string | null = null
    private taskId: string | number | null = null

    private async formChangeTask() {
        const form = document.getElementById("change_task-form") as HTMLFormElement;

        form.addEventListener("submit", async (e) => {
            e.preventDefault();

            const title = (document.getElementById("title") as HTMLInputElement).value;
            const description = (document.getElementById("description") as HTMLInputElement).value;

            if (this.checkChange(title, description)) {
                const response = await securedApiCall("todo/change", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        title,
                        description,
                        "task_id": this.taskId
                    })
                });

                if (response && response.ok) {
                    const data = await response.json();
        
                    if (data.success) {
                        alert(data.message);
                        window.location.reload();
                        return;
                    
                    } else {
                        alert(data.message);
                        return;
                    }
        
                } else {
                    console.error("Ошибка возврат данных todo/change");
                    return; 
                }
            }
        })
    }

    private async getElemTask() {
        const response = await securedApiCall("/todo/data/change");

        if (response && response.ok) {
            const data = await response.json();

            if (data.success) {
                return data;
            
            } else {
                console.error("Ошибка при возврате данных из /todo/data/change")
                return;
            }

        } else {
            console.error("Ошибка возврат данных /todo/data/change");
            return; 
        }
    }

    private checkChange(title: string, description: string) {
        return (
            title !== this.oldTitle || description !== this.oldDescription
        )
    }

    async init() {
        const data = await checkUpdateTokens();
        if (!data || !data.user_id) {
            console.error(`Ошибка при возврате функции checkUpdateTokens: ${data}`);
            return;
        };

        const dataElem = await this.getElemTask();
        if (dataElem) {
            this.oldDescription = dataElem.description
            this.oldTitle = dataElem.title
            this.taskId = dataElem.task_id

            const titleInput = document.getElementById("title") as HTMLInputElement;
            const descriptionTextarea = document.getElementById("description") as HTMLTextAreaElement;
            
            if (titleInput && descriptionTextarea) {
                titleInput.value = dataElem.title;
                descriptionTextarea.value = dataElem.description;
            }

        } else {
            console.error("Вернулись пустые данные в функции getElemTask");
            return;
        }

        await this.formChangeTask();
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const change = new ChangeTask;
    await change.init();
})