$(document).ready(function () {
    $('.sidenav').sidenav({edge: 'right'});
    $('.collapsible').collapsible();
    $('.tooltipped').tooltip();
    $('.datepicker').datepicker({
        format:"dd mmm, yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: "Select"
        }
    });
    $('select').formSelect();
});

function add(event) {
    console.log(event.target);
    let element = event.target.parentNode;
    let newElement = element.cloneNode(true);
    newElement.querySelector("input").value = "";
    // document.createElement("li");
    // newElement.classList.add("row");
    // newElement.innerHTML = `<input class="col s10" type="text" name="ingedient">
    //     <i class="col s1 center-align material-icons add" onclick="add(event)">add</i>
    //     <i class="col s1 center-align material-icons remove" onclick="remove(event)">remove</i>`
    element.insertAdjacentElement('afterend', newElement);
}

function remove(event) {
    console.log(event.target);
    let element = event.target.parentNode;
    element.remove();}

function showModal(event) {
    modal = event.target.nextElementSibling;
    console.log(modal);
    modal.classList.remove("hidden")
}