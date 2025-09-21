const REFRESH_TOKEN_KEY = 'refreshToken';
const ACCESS_TOKEN_KEY = 'accessToken';

async function updateTokens(currentRefreshToken: string): Promise<{accessToken: string; refreshToken: string}> {
    try {
        const response = await fetch('/refresh', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({refresh_token: currentRefreshToken}),
        });

        if (!response.ok) {
            const errorData = await response.json();
            if (response.status === 401 && typeof errorData.detail === 'string' && errorData.detail.includes("Refresh token")) {
                console.error("Refresh token истек. Перенаправление на страницу входа.");
                clearTokensAndRedirectLogin();
            } else {
                console.error("Ошибка при обновлении токенов:", errorData.detail || response.statusText);
                throw new Error(errorData.detail || `${'Server error'}`);
            }
        }

        const data = await response.json();
        return {
            accessToken: data.access_token,
            refreshToken: data.refresh_token,
        };
    } catch (error) {
        console.error("Ошибка в функции refreshTokens:\n", error);
        throw new Error('Server error');
    }
}

function clearTokensAndRedirectLogin() {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.location.href = '/login';
}

async function updateAccess(currentRefreshToken: string): Promise<{accessToken: string}> {
    const response = await fetch("/access", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({refresh_token: currentRefreshToken})
    })

    console.log(`ACCESS_TOKEN_KEY: ${localStorage.getItem(ACCESS_TOKEN_KEY)}\n REFRESH_TOKEN_KEY: ${localStorage.getItem(REFRESH_TOKEN_KEY)}`)
    if (response.status === 401) {
        console.error("Refresh token истек при попытке получить новый Access token. Перенаправление на страницу входа.");
        clearTokensAndRedirectLogin();
        throw new Error("Refresh token expire");
    }
    if (response.status === 500 || !response.ok) {
        throw new Error('Server error');
    }

    const data = await response.json();
    return {
        accessToken: data.access_token
    }
}

async function securedApiCall(url_api: string, options: RequestInit = {}) {
    let accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
    let refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);

    if (!refreshToken) {
        console.error("Не найден refreshToken")
        clearTokensAndRedirectLogin();
        return;
    }

    let response = await fetch(url_api, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${accessToken}`,
        },
    });
    // User not authenticated
    if (response.status === 401) {
        try {
            const newAccess = await updateAccess(refreshToken);
            localStorage.setItem(ACCESS_TOKEN_KEY, newAccess.accessToken);

            response = await fetch(url_api, {
                ...options,
                headers: {
                    ...options.headers,
                    'Authorization': `Bearer ${newAccess.accessToken}`,
                },
            });
        } catch (accessError) {
            console.error("Не удалось обновить токен:", accessError);
            clearTokensAndRedirectLogin();
            return;
        }
    }
    // rate limit (custom Retry-After)
    if (response.status === 429) {
        const retryAfterHeader = response.headers.get("Retry-After");
        const delay = retryAfterHeader ? parseInt(retryAfterHeader) : 10;
        
        console.warn(`Получен 429 Too Many Requests. Повторная попытка через ${delay} секунд.`);
        await new Promise(resolve => setTimeout(resolve, delay * 1000));
        
        return securedApiCall(url_api, options);
    }

    if (!response.ok) {
        console.error("API вызов завершился неудачей после попытки обновления токена.", response);
        return;
    }

    return response;
}

async function checkUpdateTokens() {
    try {
        const response = await securedApiCall("/check_update_tokens",{
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
        });
        if (response && response.ok) {
            if (response.status === 401 || response.status === 404) {
                console.error("Токены не были проверены. Они истекли либо не найден юзер.");
                return;
            }
            const data = await response.json();
            console.log(`Токены юзера ${data.user_id} успешно проверены`);
            return data;
        } else {
            console.error("Api вызов не был получен из securedApiCall check_update_tokens.");
            return;
        }
    } catch (error) {
        console.error('Ошибка проверки токенов:', error);
        clearTokensAndRedirectLogin();
        return;
    }
}

async function DeleteTokenRedis(
    user_id: string | number,
    token: string,
    handle: string,
) {
    const responseDelete = await securedApiCall("/confirm_code/delete_token", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            user_id,
            "token": token,
            "handle": handle
        })
    })

    if (responseDelete && responseDelete.ok) {
        const data = await responseDelete.json();

        return data;

    } else {
        console.error("Запрос /confirm_code/delete_token завершился неудачей");
        return;
    }
}

export {
    securedApiCall, 
    updateTokens, 
    clearTokensAndRedirectLogin, 
    updateAccess, 
    checkUpdateTokens,
    DeleteTokenRedis,
    REFRESH_TOKEN_KEY,
    ACCESS_TOKEN_KEY
};   