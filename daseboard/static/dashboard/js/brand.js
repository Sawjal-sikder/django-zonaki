let currentPage = 1;
const itemsPerPage = 10;
let allbrands = []; // This will store all the brands fetched from the server

// Function to populate the table with brands
function populateTable(brands) {
    const tableBody = document.querySelector('#productorder tbody');
    tableBody.innerHTML = '';

    if (brands.length === 0) {
        const nobrandsRow = document.createElement('tr');
        const nobrandsCell = document.createElement('td');
        nobrandsCell.colSpan = 6;
        nobrandsCell.textContent = 'No brands found';
        nobrandsRow.appendChild(nobrandsCell);
        tableBody.appendChild(nobrandsRow);
        return;
    }
    //console.log(JSON.stringify(brands));
    brands.forEach(brand => {
      const newRow = document.createElement('tr');
        newRow.dataset.brandId = brand.id;

        const checkBoxCell = document.createElement('td');
        const checkInput = document.createElement('input');
        checkInput.type = 'checkbox';
        checkInput.id = `brand${brand.id}`;
        checkInput.className = 'form-check-input';
        checkInput.name = 'selected_brands';
        checkInput.value = brand.id;

        const checkLabel = document.createElement('label');
        checkLabel.htmlFor = `brand${brand.id}`;

        checkBoxCell.appendChild(checkInput);
        checkBoxCell.appendChild(checkLabel);
        newRow.appendChild(checkBoxCell);
        
        console.log(JSON.stringify(brand.image));
        newRow.innerHTML += `
            <td>${brand.id}</td>
            <td>${brand.name}</td>
            <td>
              <img src="/media/${brand.image ? brand.image : 'placeholder.jpg'}" alt="${brand.image ? 'Brand Image' : 'No Image'}" style="width: 30px;"/>
            </td>
            `;

        const statusCell = document.createElement('td');
        const statusButton = document.createElement('button');
        statusButton.className = `btn btn-sm ${brand.is_verified ? 'btn-success' : 'btn-danger'}`;
        statusButton.textContent = brand.is_verified ? 'Verified' : 'Pending';
        statusCell.appendChild(statusButton);
        newRow.appendChild(statusCell);

        // newRow.innerHTML += `<td>${brand.commission}%</td>`;


        const actionsCell = document.createElement('td');
        const editLink = document.createElement('a');
        editLink.href = `/dashboard/brands/${brand.slug}/update`;
        editLink.className = 'text-info';
        editLink.innerHTML = '<i class="ti-marker-alt"></i>';

        const deleteLink = document.createElement('a');
        deleteLink.href = `/dashboard/brands/${brand.slug}/delete`;
        deleteLink.className = 'text-danger ms-5';
        deleteLink.innerHTML = '<i class="ti-trash"></i>';

        actionsCell.appendChild(editLink);
        actionsCell.appendChild(deleteLink);
        newRow.appendChild(actionsCell);

        tableBody.appendChild(newRow);
    });
}

// Function to get paginated brands
function paginate(brands, page = 1) {
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = page * itemsPerPage;
    return brands.slice(startIndex, endIndex);
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
    if (page < 1 || page > Math.ceil(allbrands.length / itemsPerPage)) return;
    currentPage = page;
    const paginatedbrands = paginate(allbrands, currentPage);
    populateTable(paginatedbrands);
    updatePaginationControls(allbrands.length);
}

// Function to handle filtering and fetching data
function filterbrands(event) {
    const status = event.target.value;
    //console.log(`status: ${status}`);
    
    fetch(`/dashboard/brands/filter/?status=${status}`)
        .then(response => response.json())
        .then(data => {
            allbrands = data.brands; // Store fetched brands
            //console.log(JSON.stringify(allbrands));
            const paginatedbrands = paginate(allbrands, currentPage);
            populateTable(paginatedbrands);
            updatePaginationControls(allbrands.length);
        })
        .catch(error => {
            console.error(error);
        });
}

// Initial setup
window.onload = () => {
    const catFilter = document.querySelectorAll('[name="status"]');

    for (const iterator of catFilter) {
        iterator.addEventListener('change', filterbrands);
        if (iterator.checked) {
            filterbrands({ target: iterator }); // Trigger change event for checked boxes
        }
    }

    // Event listeners for previous/next buttons
    document.getElementById('previous-page').addEventListener('click', () => {
        if (currentPage > 1) goToPage(currentPage - 1);
    });
    document.getElementById('next-page').addEventListener('click', () => {
        const totalPages = Math.ceil(allbrands.length / itemsPerPage);
        if (currentPage < totalPages) goToPage(currentPage + 1);
    });
};


// =======================================================================
// =======================================================================
// =======================================================================

// let currentPage = 1;
// const itemsPerPage = 10;
// let allbrands = []; // This will store all the categories fetched from the server

// // Function to populate the table with categories
// function populateTable(categories) {
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

// // Function to get paginated categories
// function paginate(categories, page = 1) {
//     const startIndex = (page - 1) * itemsPerPage;
//     const endIndex = page * itemsPerPage;
//     return categories.slice(startIndex, endIndex);
// }

// // Function to update pagination controls
// function updatePaginationControls(totalItems) {
//     const totalPages = Math.ceil(totalItems / itemsPerPage);
//     const paginationContainer = document.querySelector('.pagination-container .pagination');

//     // Clear existing page numbers
//     paginationContainer.querySelectorAll('.page-number').forEach(el => el.remove());

//     // Generate page numbers
//     for (let i = 1; i <= totalPages; i++) {
//         const pageItem = document.createElement('li');
//         pageItem.className = `page-item page-number${i === currentPage ? ' active' : ''}`;
//         pageItem.innerHTML = `<a class="page-link" href="#">${i}</a>`;
//         pageItem.addEventListener('click', () => goToPage(i));
//         paginationContainer.insertBefore(pageItem, document.getElementById('next-page'));
//     }

//     // Enable/Disable previous button
//     document.getElementById('previous-page').classList.toggle('disabled', currentPage === 1);

//     // Enable/Disable next button
//     document.getElementById('next-page').classList.toggle('disabled', currentPage === totalPages);
// }

// // Function to handle page change
// function goToPage(page) {
//     if (page < 1 || page > Math.ceil(allbrands.length / itemsPerPage)) return;
//     currentPage = page;
//     const paginatedCategories = paginate(allbrands, currentPage);
//     populateTable(paginatedCategories);
//     updatePaginationControls(allbrands.length);
// }

// // Function to handle filtering and fetching data
// function filterCategories(event) {
//     const status = event.target.value;
//     console.log(`status: ${status}`);
    
//     fetch(`/dashboard/categories/filter/?status=${status}`)
//         .then(response => response.json())
//         .then(data => {
//             allbrands = data.categories; // Store fetched categories
//             const paginatedCategories = paginate(allbrands, currentPage);
//             populateTable(paginatedCategories);
//             updatePaginationControls(allbrands.length);
//         })
//         .catch(error => {
//             console.error(error);
//         });
// }

// // Initial setup
// window.onload = () => {
//     const catFilter = document.querySelectorAll('[name="status"]');

//     for (const iterator of catFilter) {
//         iterator.addEventListener('change', filterCategories);
//         if (iterator.checked) {
//             filterCategories({ target: iterator }); // Trigger change event for checked boxes
//         }
//     }

//     // Event listeners for previous/next buttons
//     document.getElementById('previous-page').addEventListener('click', () => {
//         if (currentPage > 1) goToPage(currentPage - 1);
//     });
//     document.getElementById('next-page').addEventListener('click', () => {
//         const totalPages = Math.ceil(allbrands.length / itemsPerPage);
//         if (currentPage < totalPages) goToPage(currentPage + 1);
//     });
// };
