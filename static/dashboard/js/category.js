let currentPage = 1;
const itemsPerPage = 10;
let allCategories = []; // This will store all the categories fetched from the server

// Function to populate the table with categories
function populateTable(categories) {
    const tableBody = document.querySelector('#productorder tbody');
    tableBody.innerHTML = ''; // Clear the table body

    if (categories.length === 0) {
        const noCategoriesRow = document.createElement('tr');
        const noCategoriesCell = document.createElement('td');
        noCategoriesCell.colSpan = 6;
        noCategoriesCell.textContent = 'No categories found';
        noCategoriesRow.appendChild(noCategoriesCell);
        tableBody.appendChild(noCategoriesRow);
        return;
    }

    categories.forEach(category => {
        const newRow = document.createElement('tr');
        newRow.dataset.categoryId = category.id;

        const checkBoxCell = document.createElement('td');
        const checkInput = document.createElement('input');
        checkInput.type = 'checkbox';
        checkInput.id = `Category${category.id}`;
        checkInput.className = 'form-check-input';
        checkInput.name = 'seleted_category';
        checkInput.value = category.id;

        const checkLabel = document.createElement('label');
        checkLabel.htmlFor = `Category${category.id}`;

        checkBoxCell.appendChild(checkInput);
        checkBoxCell.appendChild(checkLabel);
        newRow.appendChild(checkBoxCell);

        newRow.innerHTML += `
            <td>${category.id}</td>
            <td>${category.category_name}</td>
            <td>${category.parent ? category.parent.category_name : 'No Parent'}</td>
        `;

        const statusCell = document.createElement('td');
        const statusButton = document.createElement('button');
        statusButton.className = `btn btn-sm ${category.is_verified ? 'btn-success' : 'btn-danger'}`;
        statusButton.textContent = category.is_verified ? 'Verified' : 'Pending';
        statusCell.appendChild(statusButton);
        newRow.appendChild(statusCell);

        newRow.innerHTML += `<td>${category.commission}%</td>`;

        const actionsCell = document.createElement('td');
        const editLink = document.createElement('a');
        editLink.href = `/dashboard/categories/${category.id}/update`;
        editLink.className = 'text-info';
        editLink.innerHTML = '<i class="ti-marker-alt"></i>';

        const deleteLink = document.createElement('a');
        deleteLink.href = `/dashboard/categories/${category.id}/delete`;
        deleteLink.className = 'text-danger ms-5';
        deleteLink.innerHTML = '<i class="ti-trash"></i>';

        actionsCell.appendChild(editLink);
        actionsCell.appendChild(deleteLink);
        newRow.appendChild(actionsCell);

        tableBody.appendChild(newRow);
    });
}

// Function to get paginated categories
function paginate(categories, page = 1) {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = page * itemsPerPage;
    return categories.slice(startIndex, endIndex);
}

// Function to update pagination controls
function updatePaginationControls(totalItems) {
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    const paginationContainer = document.querySelector('.pagination-container .pagination');

    // Clear existing page numbers
    paginationContainer.querySelectorAll('.page-number').forEach(el => el.remove());

    // Generate page numbers
    for (let i = 1; i <= totalPages; i++) {
        const pageItem = document.createElement('li');
        pageItem.className = `page-item page-number${i === currentPage ? ' active' : ''}`;
        pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
        pageItem.addEventListener('click', () => goToPage(i));
        paginationContainer.insertBefore(pageItem, document.getElementById('next-page'));
    }

    // Enable/Disable previous button
    document.getElementById('previous-page').classList.toggle('disabled', currentPage === 1);

    // Enable/Disable next button
    document.getElementById('next-page').classList.toggle('disabled', currentPage === totalPages);
}

// Function to handle page change
function goToPage(page) {
    if (page < 1 || page > Math.ceil(allCategories.length / itemsPerPage)) return;
    currentPage = page;
    const paginatedCategories = paginate(allCategories, currentPage);
    populateTable(paginatedCategories);
    updatePaginationControls(allCategories.length);
}

// Function to handle filtering and fetching data
function filterCategories(event) {
    const status = event.target.value;
    //console.log(`status: ${status}`);
    
    fetch(`/dashboard/categories/filter/?status=${status}`)
        .then(response => response.json())
        .then(data => {
            allCategories = data.categories; // Store fetched categories
            const paginatedCategories = paginate(allCategories, currentPage);
            populateTable(paginatedCategories);
            updatePaginationControls(allCategories.length);
        })
        .catch(error => {
            console.error(error);
        });
}

// Initial setup
window.onload = () => {
    const catFilter = document.querySelectorAll('[name="status"]');

    for (const iterator of catFilter) {
        iterator.addEventListener('change', filterCategories);
        if (iterator.checked) {
            filterCategories({ target: iterator }); // Trigger change event for checked boxes
        }
    }

    // Event listeners for previous/next buttons
    document.getElementById('previous-page').addEventListener('click', () => {
        if (currentPage > 1) goToPage(currentPage - 1);
    });
    document.getElementById('next-page').addEventListener('click', () => {
        const totalPages = Math.ceil(allCategories.length / itemsPerPage);
        if (currentPage < totalPages) goToPage(currentPage + 1);
    });
};




// =======================================================================
// =======================================================================
// =======================================================================

// function populateTable(categories) {
//     console.log(categories);
//     const tableBody = document.querySelector('#productorder tbody');
//     tableBody.innerHTML = ''; // Clear the table body

//     if (categories.length === 0) {
//         const noCategoriesRow = document.createElement('tr');
//         const noCategoriesCell = document.createElement('td');
//         noCategoriesCell.colSpan = 6;
//         noCategoriesCell.textContent = 'No categories found';
//         noCategoriesRow.appendChild(noCategoriesCell);
//         tableBody.appendChild(noCategoriesRow);
//         return;
//     }

//     categories.forEach(category => {
//         const newRow = document.createElement('tr');
//         newRow.dataset.categoryId = category.id;

//         const checkBoxCell = document.createElement('td');
//         const checkInput = document.createElement('input');
//         checkInput.type = 'checkbox';
//         checkInput.id = `Category${category.id}`;
//         checkInput.className = 'form-check-input';
//         checkInput.name = 'seleted_category';
//         checkInput.value = category.id;

//         const checkLabel = document.createElement('label');
//         checkLabel.htmlFor = `Category${category.id}`;

//         checkBoxCell.appendChild(checkInput);
//         checkBoxCell.appendChild(checkLabel);
//         newRow.appendChild(checkBoxCell);

//         newRow.innerHTML += `
//             <td>${category.id}</td>
//             <td>${category.category_name}</td>
//             <td>${category.parent ? category.parent.category_name : 'No Parent'}</td>
//         `;

//         const statusCell = document.createElement('td');
//         const statusButton = document.createElement('button');
//         statusButton.className = `btn btn-sm ${category.is_verified ? 'btn-success' : 'btn-danger'}`;
//         statusButton.textContent = category.is_verified ? 'Verified' : 'Pending';
//         statusCell.appendChild(statusButton);
//         newRow.appendChild(statusCell);

//         newRow.innerHTML += `<td>${category.commission}%</td>`;

//         const actionsCell = document.createElement('td');
//         const editLink = document.createElement('a');
//         editLink.href = `/dashboard/categories/${category.id}/update`;
//         editLink.className = 'text-info';
//         editLink.innerHTML = '<i class="ti-marker-alt"></i>';

//         const deleteLink = document.createElement('a');
//         deleteLink.href = `/dashboard/categories/${category.id}/delete`;
//         deleteLink.className = 'text-danger ms-5';
//         deleteLink.innerHTML = '<i class="ti-trash"></i>';

//         actionsCell.appendChild(editLink);
//         actionsCell.appendChild(deleteLink);
//         newRow.appendChild(actionsCell);

//         tableBody.appendChild(newRow);
//     });
// }


// window.onload = () => {
//     const catFilter = document.querySelectorAll('[name="status"]');
//     // Function to handle filtering and fetching data
//     function filterCategories(event) {
//         const status = event.target.value;
//         console.log(`status: ${status}`);
//         if (event.target.checked) {
//             console.log(`event.checked: ${status}`);
//         }

//         fetch(`/dashboard/categories/filter/?status=${status}`)
//             .then(response => response.json())
//             .then(data => {
//                 populateTable(data.categories);
//             })
//             .catch(error => {
//                 console.error(error);
//             });
//     }

//     for (const iterator of catFilter) {
//         iterator.addEventListener('change', filterCategories);
//         if (iterator.checked) {
//             filterCategories({ target: iterator }); // Trigger change event for checked boxes
//         }
//     }
// };


//===================================================================================
//===================================================================================
//===================================================================================

// function populateTable(categories) {

//     console.log(categories);
//     const tableBody = $('#productorder tbody');
//     tableBody.empty();

//     if (categories.length === 0) {
//         tableBody.append('<tr><td colspan="6">No categories found</td></tr>');
//         return;
//     }

//     categories.forEach(category => {
//         const newRow = $('<tr></tr>');
//         newRow.data('category-id', category.id);

//         const checkBox = $(`<td></td>`);
//         const checkInput = $(`<input type="checkbox" id="Category${category.id}" class="form-check-input" name="seleted_category" value="${category.id}">`);
//         const checkLabel = $(`<label for="Category${category.id}"></label>`);
//         checkBox.append(checkInput);
//         checkBox.append(checkLabel);
//         newRow.append(checkBox);
//         newRow.append(`<td>${category.id}</td>`);
//         newRow.append(`<td>${category.category_name}</td>`);
//         newRow.append(`<td>${category.parent ? category.parent.category_name : 'No Parent'}</td>`);

//         const statusCell = $('<td></td>');
//         const statusButton = $('<button class="btn btn-sm"></button>');
//         statusButton.text(category.is_verified ? 'Verified' : 'Pending');
//         statusButton.addClass(category.is_verified ? 'btn-success' : 'btn-danger');
//         statusCell.append(statusButton);
//         newRow.append(statusCell);

//         newRow.append(`<td>${category.commission}%</td>`);

//         const actionsCell = $('<td></td>');
//         const editLink = $(`<a href="/dashboard/categories/${category.id}/update" class="text-info"><i class="ti-marker-alt"></i></a>`);
//         const deleteLink = $(`<a href="/dashboard/categories/${category.id}/delete" class="text-danger ms-5"><i class="ti-trash"></i></a>`);
//         actionsCell.append(editLink);
//         actionsCell.append(deleteLink);
//         newRow.append(actionsCell);

//         tableBody.append(newRow);
//     });
// }

// window.onload = () => {
//     const catFilter = document.querySelectorAll('[name="status"]');

//     // Function to handle filtering and fetching data
//     function filterCategories(event) {
//         const status = event.target.value;
//         console.log(`status: ${status}`);
//         if (event.target.checked) {
//             console.log(`event.checked: ${status}`);
//         }

//         fetch(`/dashboard/categories/filter/?status=${status}`)
//             .then(response => response.json())
//             .then(data => {
//                 populateTable(data.categories);
//             })
//             .catch(error => {
//                 console.error(error);
//             });
//     }

//     for (const iterator of catFilter) {
//         iterator.addEventListener('change', filterCategories);
//         if (iterator.checked) {
//             filterCategories({ target: iterator }); // Trigger change event for checked boxes
//         }
//     }
// };

// window.onload = () => {
//     const catFilter = document.querySelectorAll('[name="status"]');

//     for (const iterator of catFilter) {
//         iterator.addEventListener('change', function (event) {
//             const status = event.target.value;

//             fetch(`/dashboard/categories/filter/?status=${status}`)

//             .then(response => response.json())
//             .then(data => {
//                 populateTable(data.categories);
//             })
//             .catch(error => {
//                 console.log(error);
//             });
//         });
//     }
// };