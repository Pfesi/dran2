const list = document.getElementById("list");
const pagination = document.getElementById("pagination");
const itemsPerPageSelect = document.getElementById("itemsPerPage");

let itemsPerPage = parseInt(itemsPerPageSelect.value);
//Number of items per page
let currentPage = 1; //current page
let data = []; //array of data items

//generate dummy data
for (let i = 1; i < 20; i++) {
    data.push(`Item ${i}`);
}

// Display data on initial page load
displayData();

// Pagination click event handler
pagination.addEventListener('click', function (e) {
    if (e.target.tagName === 'SPAN') {
        currentPage = parseInt(e.target.textContent);
        displayData();
    }
});

//Items per page select change event handler
itemsPerPageSelect.addEventListener('change', function(e) {
    itemsPerPage = parseInt(e.target.value);
    currentPage = 1; //reset to first page
    displayData();
});

// Function to display data on the current page
function displayData() {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = data.slice(startIndex, endIndex);

    // clear list and pagination
    list.innerHTML = '';
    pagination.innerHTML = '';

    // Display paginated data with animation
    paginatedData.forEach((item, index) => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);

        // apply fade-in animation class for each item
        setTimeout(() => {
            li.classList.add('fade-in');
        }, index * 100);
        
    });

    // Generate pagination links
    const totalPages = Math.ceil(data.length / itemsPerPage);
    for (let i = 1; i <= totalPages; i++) {
        const pageLink = document.createElement('span');
        pageLink.textContent = i;
        if (i === currentPage) {
            pageLink.classList.add('pagination','active');
        } else {
            pageLink.classList.add('pagination');
        }
        pagination.appendChild(pageLink);
    }
}