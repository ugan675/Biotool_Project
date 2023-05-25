const searchField = document.querySelector("#search-field");
const outputArea = document.querySelector(".files");
const originalHTML = outputArea.innerHTML;
const pk = "search-field";
var URL = "/";

const searchFieldTools = document.querySelector("#search-field-tools");
const outputAreaTools = document.querySelector(".tools");
const originalHTMLTools = outputAreaTools.innerHTML;
const pkTools = "search-field-tools";

function clearSearchTools() {
    searchFieldTools.value = '';
    outputAreaTools.innerHTML = originalHTMLTools;
}

searchFieldTools.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    if (searchValue.length > 0) {
        fetch('/', {
            body: JSON.stringify({id: "search-field-tools", searchText: searchValue}),
            method: "POST",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            },
        })
        .then((res) => res.json())
        .then((data) => {
            if (data.tools.length === 0) {
                outputAreaTools.innerHTML = "<p class='files_displayed'>No results found</p>";
                //'<button href="" id="upload" onclick="uploadClicked(this.id)" class="tool_ref">upload</button>'
            } else {
                outputAreaTools.innerHTML = '';
                data.tools.forEach((item) => {
                    outputAreaTools.innerHTML += '<button href="" id="' + item + '" onclick="addcmd(this.id)" class="tool_ref">' + item + '</button>';
                });
            }
        });
    } else {
        outputAreaTools.innerHTML = originalHTMLTools;
    }
});

function clearSearch() {
    searchField.value = '';
    outputArea.innerHTML = originalHTML;
}

searchField.addEventListener('keyup', (e) => {
    const searchValue = e.target.value;
    if (searchValue.length > 0) {
        fetch('/', {
                body: JSON.stringify({id: "search-field", searchText: searchValue}),
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
            .then((res) => res.json())
            .then((data) => {
                if (data.files.length === 0) {
                    outputArea.innerHTML = "<p class='files_displayed'>No results found</p>"
                } else {
                    outputArea.innerHTML = '';
                    data.files.forEach((item) => {
                        outputArea.innerHTML += "<p class='files_displayed'>" + item + "</p>";
                    });
                }
            });
    } else {
        outputArea.innerHTML = originalHTML;
    }

});
