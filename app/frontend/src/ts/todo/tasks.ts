import { checkUpdateTokens, securedApiCall } from "../utils/security.js";

class TodoTasks {
    private tasksArray: Array<{ title: string; description: string; status: boolean; id_todo: number; }> | null = null 
    private isTasks: boolean = false

    private async getTasksDB() {
        const response = await securedApiCall("/todo/tasks/data");

        if (response && response.ok) {
            const dataTasks = await response.json();

            if (dataTasks.success && dataTasks.todo && dataTasks.todo.length > 0) {
                this.isTasks = true;
                this.tasksArray = dataTasks.todo;

            } else {
                this.isTasks = false;
                this.tasksArray = null;
            }     

        } else {
            console.error("Ошибка возврат данных /todo/tasks/data");
            return;
        }
    }

    private async tasksPage() {
        const tasks = document.getElementById("tasks") as HTMLDivElement;

        if (!this.isTasks && !this.tasksArray) {
            tasks.innerHTML = `
            <p>Нет добавленных задач.</p>
            <a href="/todo/create">Создать задачу</a>
            `
            
        } else if (this.tasksArray) {
            let resultHtml = `<a href="/todo/create">Создать еще</a>`

            for (let task of this.tasksArray) {
                const title = task.title;
                const description = task.description;
                const status = task.status;
                const id_todo = task.id_todo;
                let statusStr
                
                if (status == true) {
                    statusStr = "Выполнена"
                } else {
                    statusStr = "Не выполнена"
                }

                resultHtml += `
                <div id="title" class="row">
                    <h4>Title:</h4>
                    <span>${title}</span>
                </div>

                <div id="description">
                    <h5>description:</h5> ${description}
                </div>

                <div id="status" class="row">
                    <h5>status:</h5>
                    <span>${statusStr}</span>
                </div>

                <div id="id_todo" class="row">
                    <h6>id:</h6> 
                    <span>${id_todo}</span>
                </div>

                <form class="task_control-form" data-task-id="${id_todo}">
                    <button type="button" data-action="change">Изменить</button>
                    <button type="button" data-action="status_task">${status === true ? "Не выполнено" : "Выполнено"}</button>
                    <button type="button" data-action="delete">Удалить</button>
                </form>
                `
            }
            tasks.innerHTML = resultHtml
        }
    }

    private async eventChangeTask(taskId: string) {
        window.location.href = `/todo/change?task_id=${taskId}`;
        return;
    }

    private async eventStatusTask(taskId: string) {
        const response = await securedApiCall("/todo/change_status", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: taskId
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
            console.error("Ошибка возврат данных todo/change_status");
            return; 
        }
    }

    private async eventDeleteTask(taskId: string) {
        const response = await securedApiCall("/todo/delete", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: taskId
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
            console.error("Ошибка возврат данных todo/delete");
            return; 
        }
    }

    private async buttonTaskControl() {
        const tasksElement = document.getElementById("tasks") as HTMLDivElement;
        
        if (tasksElement) {
            tasksElement.addEventListener("click", async (event) => {
                const target = event.target as HTMLElement;
                
                if (target.tagName === "BUTTON") {
                    const form = target.closest(".task_control-form") as HTMLFormElement;
                    
                    if (form) {
                        const taskId = form.dataset.taskId;
                        const action = target.dataset.action;

                        if (taskId && action) {
                            switch (action) {
                                case "change":
                                    await this.eventChangeTask(taskId);
                                    break;

                                case "status_task":
                                    await this.eventStatusTask(taskId);
                                    break;

                                case "delete":
                                    await this.eventDeleteTask(taskId);
                                    break;
                            }
                        }
                    }
                }
            });
        }
    }

    async init() {
        const data = await checkUpdateTokens();
        if (!data || !data.user_id) {
            console.error(`Ошибка при возврате функции checkUpdateTokens: ${data}`);
            return;
        };

        await this.getTasksDB();

        await this.tasksPage();

        await this.buttonTaskControl();
    }  
}



document.addEventListener("DOMContentLoaded", async () => {
    const tasks = new TodoTasks;
    await tasks.init();
})