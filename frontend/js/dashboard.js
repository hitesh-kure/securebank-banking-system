
const API_BASE_URL = "http://127.0.0.1:8000";

// Get the JWT access token saved during login
const accessToken = sessionStorage.getItem("accessToken");

// Logout functionality
const logoutButton = document.getElementById("logoutButton");

if (logoutButton) {
  logoutButton.addEventListener("click", function () {
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("refreshToken");
    sessionStorage.removeItem("access");
    sessionStorage.removeItem("refresh");

    window.location.href = "index.html";
  });
}

// Get dashboard HTML elements
const accountBalance = document.getElementById("accountBalance");
const accountStatus = document.getElementById("accountStatus");
const transactionMessage = document.getElementById("transactionMessage");

// Store transactions for the current page
let allTransactions = [];
let currentPage = 1;
let totalTransactions = 0;
let nextPageUrl = null;
let previousPageUrl = null;

// Reusable success popup
function showSuccessPopup(title, description) {
  document.getElementById("successTitle").textContent = title;
  document.getElementById("successDescription").textContent = description;
  document.getElementById("successPopup").style.display = "flex";
}

// Close success popup
document
  .getElementById("successOkButton")
  .addEventListener("click", function () {
    document.getElementById("successPopup").style.display = "none";
  });

// Check login status
if (!accessToken) {
  window.location.href = "index.html";
}

// Fetch account details
async function loadAccountDetails() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/accounts/`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      console.error("Failed to load accounts:", response.status);
      accountStatus.textContent = "Unable to load account";

      transactionMessage.textContent =
        response.status === 401
          ? "Your session may have expired. Please log in again."
          : "Unable to load account details.";

      return;
    }

    const accounts = await response.json();

    console.log("Account details:", accounts);

    if (Array.isArray(accounts) && accounts.length > 0) {
      accountBalance.textContent = "₹" + accounts[0].balance;
      window.accountNumber = accounts[0].account_number;
      accountStatus.textContent = accounts[0].status;

      await loadTransactions(accounts[0].account_number);
    } else {
      accountBalance.textContent = "No account found";
      accountStatus.textContent = "N/A";
      transactionMessage.textContent = "No account found.";
    }
  } catch (error) {
    console.error("Error connecting to Django:", error);
    accountStatus.textContent = "Connection error";
    transactionMessage.textContent = "Unable to connect to the server.";
  }
}

// Create pagination controls
function createPaginationControls() {
  const tableBody = document.getElementById("transactionTableBody");

  if (!tableBody) return;

  const table = tableBody.closest("table");

  if (!table) return;

  let paginationContainer = document.getElementById("paginationControls");

  if (!paginationContainer) {
    paginationContainer = document.createElement("div");
    paginationContainer.id = "paginationControls";
    paginationContainer.className =
      "d-flex flex-wrap justify-content-between align-items-center gap-2 mt-3 mb-3";

    table.insertAdjacentElement("afterend", paginationContainer);
  }

  paginationContainer.innerHTML = `
    <button
      type="button"
      id="previousPageButton"
      class="btn btn-outline-primary"
    >
      Previous
    </button>

    <span id="paginationInfo" class="text-muted text-center">
      Page 1
    </span>

    <button
      type="button"
      id="nextPageButton"
      class="btn btn-outline-primary"
    >
      Next
    </button>
  `;

  document
    .getElementById("previousPageButton")
    .addEventListener("click", function () {
      if (previousPageUrl) {
        loadTransactions(window.accountNumber, previousPageUrl);
      }
    });

  document
    .getElementById("nextPageButton")
    .addEventListener("click", function () {
      if (nextPageUrl) {
        loadTransactions(window.accountNumber, nextPageUrl);
      }
    });
}

// Update pagination information
function updatePaginationControls() {
  const previousButton = document.getElementById("previousPageButton");
  const nextButton = document.getElementById("nextPageButton");
  const paginationInfo = document.getElementById("paginationInfo");

  if (!previousButton || !nextButton || !paginationInfo) return;

  previousButton.disabled = !previousPageUrl;
  nextButton.disabled = !nextPageUrl;

  const start =
    totalTransactions === 0 ? 0 : (currentPage - 1) * 10 + 1;

  const end = Math.min(currentPage * 10, totalTransactions);

  paginationInfo.textContent =
    `Page ${currentPage} | Showing ${start}-${end} of ${totalTransactions} transaction(s)`;
}

// Load paginated transactions
async function loadTransactions(accountNumber, pageUrl = null) {
  try {
    transactionMessage.textContent = "Loading transactions...";

    const url =
      pageUrl ||
      `${API_BASE_URL}/api/accounts/${accountNumber}/transactions/`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      transactionMessage.textContent =
        response.status === 401
          ? "Your session may have expired. Please log in again."
          : "Unable to load transaction history.";

      console.error("Failed to load transactions:", response.status);
      return;
    }

    const data = await response.json();

    if (!data || !Array.isArray(data.results)) {
      console.error("Unexpected transaction API response:", data);

      transactionMessage.textContent =
        "The transaction response format is incorrect. Please check backend pagination.";

      return;
    }

    allTransactions = data.results;
    totalTransactions = data.count;
    nextPageUrl = data.next;
    previousPageUrl = data.previous;

    const parsedUrl = new URL(url, window.location.href);
    currentPage = Number(parsedUrl.searchParams.get("page")) || 1;

    console.log("Transaction page:", data);

    createPaginationControls();
    renderTransactions();
    updatePaginationControls();
  } catch (error) {
    console.error("Error loading transactions:", error);
    transactionMessage.textContent = "Error loading transaction history.";
  }
}

// Search and filter transactions on the current page
function renderTransactions() {
  const transactionTableBody = document.getElementById(
    "transactionTableBody"
  );

  if (!transactionTableBody) return;

  const searchInput = document.getElementById("transactionSearch");
  const typeFilter = document.getElementById("transactionTypeFilter");

  const searchText = searchInput
    ? searchInput.value.trim().toLowerCase()
    : "";

  const selectedType = typeFilter ? typeFilter.value : "ALL";

  const filteredTransactions = allTransactions.filter(function (transaction) {
    const reference = String(transaction.reference || "").toLowerCase();
    const transactionType = transaction.transaction_type || "";

    const matchesSearch = reference.includes(searchText);
    const matchesType =
      selectedType === "ALL" || transactionType === selectedType;

    return matchesSearch && matchesType;
  });

  transactionTableBody.innerHTML = "";

  if (filteredTransactions.length === 0) {
    transactionMessage.textContent =
      allTransactions.length === 0
        ? "No transactions found."
        : "No transactions on this page match your search or filter.";

    return;
  }

  transactionMessage.textContent =
    `Showing ${filteredTransactions.length} matching transaction(s) on this page.`;

  filteredTransactions.forEach(function (transaction) {
    const row = document.createElement("tr");

    const displayType = transaction.transaction_type;
    let amountDisplay = "₹" + transaction.amount;
    let typeClass = "";

    // Credited money and deposits
    if (
      transaction.transaction_type === "CREDITED" ||
      transaction.transaction_type === "DEPOSIT"
    ) {
      typeClass = "text-success fw-bold";
      amountDisplay = "+₹" + transaction.amount;
    }

    // Debited money and withdrawals
    else if (
      transaction.transaction_type === "DEBITED" ||
      transaction.transaction_type === "WITHDRAWAL"
    ) {
      typeClass = "text-danger fw-bold";
      amountDisplay = "-₹" + transaction.amount;
    }

    const typeCell = document.createElement("td");
    typeCell.className = typeClass;
    typeCell.textContent = displayType;

    const amountCell = document.createElement("td");
    amountCell.className = typeClass;
    amountCell.textContent = amountDisplay;

    const referenceCell = document.createElement("td");
    referenceCell.textContent = transaction.reference || "";

    const dateCell = document.createElement("td");
    dateCell.textContent = new Date(
      transaction.created_at
    ).toLocaleString();

    row.append(typeCell, amountCell, referenceCell, dateCell);
    transactionTableBody.appendChild(row);
  });
}

// Connect search and filter
const transactionSearch = document.getElementById("transactionSearch");

const transactionTypeFilter = document.getElementById(
  "transactionTypeFilter"
);

if (transactionSearch) {
  transactionSearch.addEventListener("input", renderTransactions);
}

if (transactionTypeFilter) {
  transactionTypeFilter.addEventListener("change", renderTransactions);
}

// Load dashboard data
if (accessToken) {
  loadAccountDetails();
}

// Deposit functionality
const depositForm = document.getElementById("depositForm");
const depositMessage = document.getElementById("depositMessage");

depositForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const amount = document.getElementById("depositAmount").value;

  depositMessage.textContent = "Processing deposit...";
  depositMessage.style.color = "blue";

  try {
    const response = await fetch(`${API_BASE_URL}/api/deposit/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        account_number: window.accountNumber,
        amount: amount,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showSuccessPopup(
        "Deposit Successful!",
        "Your money has been deposited successfully."
      );

      depositMessage.textContent = "";
      depositForm.reset();

      await loadAccountDetails();
    } else {
      depositMessage.textContent =
        data.detail || data.error || JSON.stringify(data);

      depositMessage.style.color = "red";
    }
  } catch (error) {
    depositMessage.textContent = "Unable to connect to the server.";
    depositMessage.style.color = "red";
    console.error(error);
  }
});

// Withdrawal functionality
const withdrawForm = document.getElementById("withdrawForm");
const withdrawMessage = document.getElementById("withdrawMessage");

withdrawForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const amount = document.getElementById("withdrawAmount").value;

  withdrawMessage.textContent = "Processing withdrawal...";
  withdrawMessage.style.color = "blue";

  try {
    const response = await fetch(`${API_BASE_URL}/api/withdraw/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        account_number: window.accountNumber,
        amount: amount,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showSuccessPopup(
        "Withdrawal Successful!",
        "Your money has been withdrawn successfully."
      );

      withdrawMessage.textContent = "";
      withdrawForm.reset();

      await loadAccountDetails();
    } else {
      withdrawMessage.textContent =
        data.detail || data.error || JSON.stringify(data);

      withdrawMessage.style.color = "red";
    }
  } catch (error) {
    withdrawMessage.textContent = "Unable to connect to the server.";
    withdrawMessage.style.color = "red";
    console.error(error);
  }
});

// Transfer functionality
const transferForm = document.getElementById("transferForm");
const transferMessage = document.getElementById("transferMessage");

transferForm.addEventListener("submit", async function (event) {
  event.preventDefault();

  const destinationAccount =
    document.getElementById("destinationAccount").value;

  const amount = document.getElementById("transferAmount").value;

  transferMessage.textContent = "Processing transfer...";
  transferMessage.style.color = "blue";

  try {
    const response = await fetch(`${API_BASE_URL}/api/transfer/`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        source_account_number: window.accountNumber,
        destination_account_number: destinationAccount,
        amount: amount,
      }),
    });

    const data = await response.json();

    if (response.ok) {
      showSuccessPopup(
        "Transfer Successful!",
        "Your money has been transferred successfully."
      );

      transferMessage.textContent = "";
      transferForm.reset();

      await loadAccountDetails();
    } else {
      transferMessage.textContent =
        data.detail || data.error || JSON.stringify(data);

      transferMessage.style.color = "red";
    }
  } catch (error) {
    transferMessage.textContent = "Unable to connect to the server.";
    transferMessage.style.color = "red";
    console.error(error);
  }
});

// Print Mini Statement
const printStatementButton = document.getElementById(
  "printStatementButton"
);

if (printStatementButton) {
  printStatementButton.addEventListener("click", function () {
    const accountNumber = window.accountNumber;
    const balance = accountBalance.textContent;

    if (!accountNumber) {
      alert("Account details are not loaded yet.");
      return;
    }

    const transactionTableBody = document.getElementById(
      "transactionTableBody"
    );

    if (!transactionTableBody || transactionTableBody.rows.length === 0) {
      alert("There are no transactions to print.");
      return;
    }

    const printWindow = window.open("", "_blank");

    if (!printWindow) {
      alert("Please allow pop-ups in your browser to print the statement.");
      return;
    }

    const printDate = new Date().toLocaleString();

    const printableRows = Array.from(transactionTableBody.rows)
      .map(function (row) {
        const cells = Array.from(row.cells)
          .map(function (cell) {
            return `<td>${cell.textContent}</td>`;
          })
          .join("");

        return `<tr>${cells}</tr>`;
      })
      .join("");

    printWindow.document.write(`
      <!doctype html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SecureBank Mini Statement</title>

        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 35px;
            color: #222;
          }

          h1 {
            color: #0d6efd;
            margin-bottom: 5px;
          }

          .statement-header {
            border-bottom: 2px solid #0d6efd;
            padding-bottom: 15px;
          }

          .account-details {
            margin-top: 20px;
            line-height: 1.8;
          }

          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
          }

          th, td {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: left;
            word-break: break-word;
          }

          th {
            background: #f0f4f8;
          }

          .footer {
            margin-top: 30px;
            font-size: 12px;
            color: #666;
          }

          @media print {
            body {
              margin: 15px;
            }

            th {
              background: #f0f4f8 !important;
              print-color-adjust: exact;
              -webkit-print-color-adjust: exact;
            }
          }
        </style>
      </head>

      <body>
        <div class="statement-header">
          <h1>SecureBank</h1>
          <p>Mini Account Statement</p>
        </div>

        <div class="account-details">
          <strong>Account Number:</strong> ${accountNumber}<br>
          <strong>Available Balance:</strong> ${balance}<br>
          <strong>Statement Generated:</strong> ${printDate}
        </div>

        <h2>Transaction History</h2>

        <table>
          <thead>
            <tr>
              <th>Transaction Type</th>
              <th>Amount</th>
              <th>Reference</th>
              <th>Date</th>
            </tr>
          </thead>

          <tbody>
            ${printableRows}
          </tbody>
        </table>

        <div class="footer">
          <p>This statement was generated electronically by SecureBank.</p>
        </div>
      </body>
      </html>
    `);

    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
  });
}
