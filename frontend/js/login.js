
const loginForm = document.getElementById("loginForm");
const loginMessage = document.getElementById("loginMessage");

loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    loginMessage.textContent = "Logging in...";

    try {
        const response = await fetch(
            "http://127.0.0.1:8000/api/token/",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    password: password
                })
            }
        );

        const data = await response.json();

        if (response.ok) {
            sessionStorage.setItem("accessToken", data.access);
            sessionStorage.setItem("refreshToken", data.refresh);

            window.location.href = "dashboard.html";
        } else {
            loginMessage.textContent =
                data.detail || "Login failed. Check your credentials.";
            loginMessage.style.color = "red";
        }
    } catch (error) {
        loginMessage.textContent =
            "Cannot connect to the server. Is Django running?";
        loginMessage.style.color = "red";

        console.error(error);
    }
});
