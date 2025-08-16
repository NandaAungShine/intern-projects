const addDestinationForm = document.getElementById('add-destination-form');
const addDestinationToggleBtn = document.getElementById('add-destination-toggle');
const closeDestinationFormBtn = document.getElementById('close-destination-form');
const cancelDestinationAddBtn = document.getElementById('cancel-destination-add');
const destinationFormTitle = document.getElementById('destination-form-title');

const addHotelForm = document.getElementById('add-hotel-form');
const addHotelToggleBtn = document.getElementById('add-hotel-toggle');
const closeHotelFormBtn = document.getElementById('close-hotel-form');
const cancelHotelAddBtn = document.getElementById('cancel-hotel-add');
const hotelFormTitle = document.getElementById('hotel-form-title');

function hideForm(formElement, titleElement, defaultTitle) {
    formElement.classList.add('hidden');
    titleElement.textContent = defaultTitle;
    formElement.reset();
    const fileStatusSpan = formElement.querySelector('.file-upload-text');
    if (fileStatusSpan) fileStatusSpan.textContent = 'No files selected.';
    const imagePreviewDiv = formElement.querySelector('[id$="-current-image-preview"]');
    if (imagePreviewDiv) imagePreviewDiv.style.display = 'none';

    if (formElement.id === 'add-hotel-form') {
        const roomTypesContainer = document.getElementById('room-types-container');
        while (roomTypesContainer.children.length > 1) {
            roomTypesContainer.removeChild(roomTypesContainer.lastChild);
        }
        const firstRoomTypeInputGroup = roomTypesContainer.querySelector('.room-type-input-group');
        if (firstRoomTypeInputGroup) {
            firstRoomTypeInputGroup.querySelector('.remove-room-type-btn').classList.add('hidden');
            firstRoomTypeInputGroup.querySelector('input[name="roomType[]"]').value = '';
        }
    }
}

addDestinationToggleBtn.addEventListener('click', () => {
    hideForm(addHotelForm, hotelFormTitle, 'Add New Hotel');
    addDestinationForm.classList.remove('hidden');
    destinationFormTitle.textContent = 'Add New Destination';
    document.getElementById('destination-edit-id').value = '';
    document.getElementById('destination-current-image-preview').style.display = 'none';
});
closeDestinationFormBtn.addEventListener('click', () => hideForm(addDestinationForm, destinationFormTitle, 'Add New Destination'));
cancelDestinationAddBtn.addEventListener('click', () => hideForm(addDestinationForm, destinationFormTitle, 'Add New Destination'));

addHotelToggleBtn.addEventListener('click', () => {
    hideForm(addDestinationForm, destinationFormTitle, 'Add New Destination');
    addHotelForm.classList.remove('hidden');
    hotelFormTitle.textContent = 'Add New Hotel';
    document.getElementById('hotel-edit-id').value = '';
    document.getElementById('hotel-current-image-preview').style.display = 'none';
});
closeHotelFormBtn.addEventListener('click', () => hideForm(addHotelForm, hotelFormTitle, 'Add New Hotel'));
cancelHotelAddBtn.addEventListener('click', () => hideForm(addHotelForm, hotelFormTitle, 'Add New Hotel'));


function setupFileUpload(inputId, statusId) {
    const fileInput = document.getElementById(inputId);
    const fileStatusSpan = document.getElementById(statusId);

    if (fileInput && fileStatusSpan) {
        fileInput.addEventListener('change', (event) => {
            if (event.target.files.length > 0) {
                if (event.target.files.length === 1) {
                    fileStatusSpan.textContent = event.target.files[0].name;
                } else {
                    fileStatusSpan.textContent = `${event.target.files.length} files selected.`;
                }
            } else {
                fileStatusSpan.textContent = 'No files selected.';
            }
        });
    }
}

setupFileUpload('destination-image-upload', 'destination-file-status');
setupFileUpload('hotel-image-upload', 'hotel-file-status');


const addRoomTypeBtn = document.getElementById('add-room-type-btn');
const roomTypesContainer = document.getElementById('room-types-container');

function addRoomTypeInput(value = '') {
    const newRoomTypeGroup = document.createElement('div');
    newRoomTypeGroup.classList.add('room-type-input-group');

    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'roomType[]';
    input.placeholder = 'e.g., Standard Double';
    input.value = value;

    const removeBtn = document.createElement('button');
    removeBtn.type = 'button';
    removeBtn.classList.add('remove-room-type-btn');
    removeBtn.textContent = '\u00D7';

    removeBtn.addEventListener('click', () => {
        newRoomTypeGroup.remove();
        if (roomTypesContainer.children.length === 1) {
            roomTypesContainer.querySelector('.remove-room-type-btn').classList.add('hidden');
        }
    });

    newRoomTypeGroup.appendChild(input);
    newRoomTypeGroup.appendChild(removeBtn);
    roomTypesContainer.appendChild(newRoomTypeGroup);

    if (roomTypesContainer.children.length > 1) {
        Array.from(roomTypesContainer.children).forEach(child => {
            const btn = child.querySelector('.remove-room-type-btn');
            if (btn) btn.classList.remove('hidden');
        });
    }
}

addRoomTypeBtn.addEventListener('click', () => addRoomTypeInput());

if (roomTypesContainer.children.length === 0) {
    addRoomTypeInput();
}
if (roomTypesContainer.children.length === 1) {
    roomTypesContainer.querySelector('.remove-room-type-btn').classList.add('hidden');
}


document.querySelectorAll('.edit-btn').forEach(button => {
    button.addEventListener('click', (event) => {
        const card = event.target.closest('.card');
        const cardType = event.target.dataset.type;

        if (cardType === 'destination') {
            hideForm(addHotelForm, hotelFormTitle, 'Add New Hotel');

            destinationFormTitle.textContent = 'Edit Destination';
            document.getElementById('destination-edit-id').value = card.dataset.id;
            document.getElementById('destination-name').value = card.dataset.name;
            document.getElementById('destination-contact').value = card.dataset.contact || '';
            document.getElementById('destination-tags').value = card.dataset.tags || '';
            document.getElementById('destination-description').value = card.dataset.description;
            document.getElementById('destination-country').value = card.dataset.country;
            document.getElementById('destination-season').value = card.dataset.season || '';

            const currentImagePreview = document.getElementById('destination-current-image-preview');
            const currentImage = document.getElementById('destination-current-image');
            if (card.dataset.image) {
                currentImage.src = card.dataset.image;
                currentImagePreview.style.display = 'block';
            } else {
                currentImagePreview.style.display = 'none';
            }
            document.getElementById('destination-file-status').textContent = 'No new file selected.';

            addDestinationForm.classList.remove('hidden');
        } else if (cardType === 'hotel') {
            hideForm(addDestinationForm, destinationFormTitle, 'Add New Destination');

            hotelFormTitle.textContent = 'Edit Hotel';
            document.getElementById('hotel-edit-id').value = card.dataset.id;
            document.getElementById('hotel-name').value = card.dataset.name;
            document.getElementById('hotel-contact').value = card.dataset.contact || '';
            document.getElementById('hotel-destination').value = card.dataset.destination;
            document.getElementById('hotel-rating').value = card.dataset.rating;
            document.getElementById('hotel-minprice').value = card.dataset.minprice;
            document.getElementById('hotel-maxprice').value = card.dataset.maxprice;
            document.getElementById('hotel-description').value = card.dataset.description;

            while (roomTypesContainer.children.length > 0) {
                roomTypesContainer.removeChild(roomTypesContainer.lastChild);
            }
            const roomTypes = card.dataset.roomtypes ? card.dataset.roomtypes.split(',') : [];
            if (roomTypes.length > 0) {
                roomTypes.forEach(type => addRoomTypeInput(type.trim()));
            } else {
                addRoomTypeInput();
            }
            if (roomTypesContainer.children.length === 1) {
                roomTypesContainer.querySelector('.remove-room-type-btn').classList.add('hidden');
            } else {
                Array.from(roomTypesContainer.children).forEach(child => {
                    const btn = child.querySelector('.remove-room-type-btn');
                    if (btn) btn.classList.remove('hidden');
                });
            }

            const amenitiesCheckboxes = document.querySelectorAll('#hotel-amenities input[type="checkbox"]');
            const cardAmenities = card.dataset.amenities ? card.dataset.amenities.split(',') : [];
            amenitiesCheckboxes.forEach(checkbox => {
                checkbox.checked = cardAmenities.includes(checkbox.value);
            });

            const currentImagePreview = document.getElementById('hotel-current-image-preview');
            const currentImage = document.getElementById('hotel-current-image');
            if (card.dataset.image) {
                currentImage.src = card.dataset.image;
                currentImagePreview.style.display = 'block';
            } else {
                currentImagePreview.style.display = 'none';
            }
            document.getElementById('hotel-file-status').textContent = 'No new file selected.';

            addHotelForm.classList.remove('hidden');
        }
    });
});

addDestinationForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const form = event.target;
    const id = form.querySelector('#destination-edit-id').value;
    const name = form.querySelector('#destination-name').value;
    const contact = form.querySelector('#destination-contact').value;
    const tags = form.querySelector('#destination-tags').value;
    const description = form.querySelector('#destination-description').value;
    const country = form.querySelector('#destination-country').value;
    const season = form.querySelector('#destination-season').value;
    const imageFile = form.querySelector('#destination-image-upload').files[0];

    let imageUrl = '';
    const currentImageElement = document.getElementById('destination-current-image');
    if (imageFile) {
        imageUrl = URL.createObjectURL(imageFile);
    } else if (currentImageElement && currentImageElement.src) {
        imageUrl = currentImageElement.src;
    } else {
        imageUrl = 'https://via.placeholder.com/400x240/cccccc/000000?text=No+Image';
    }


    if (id) {
        const cardToUpdate = document.querySelector(`.card[data-id="${id}"]`);
        if (cardToUpdate) {
            cardToUpdate.dataset.name = name;
            cardToUpdate.dataset.contact = contact;
            cardToUpdate.dataset.tags = tags;
            cardToUpdate.dataset.description = description;
            cardToUpdate.dataset.country = country;
            cardToUpdate.dataset.season = season;
            cardToUpdate.dataset.image = imageUrl;

            cardToUpdate.querySelector('.card-img').src = imageUrl;
            cardToUpdate.querySelector('.card-title').textContent = name;
            cardToUpdate.querySelector('.card-desc').textContent = description;
            cardToUpdate.querySelector('.contact').textContent = `📞 Contact Us: ${contact}`;
        }
    } else {
        const newCardId = `new-dest-${Date.now()}`;
        const newCardHtml = `
            <article class="card"
                     data-id="${newCardId}"
                     data-name="${name}"
                     data-country="${country}"
                     data-season="${season}"
                     data-description="${description}"
                     data-contact="${contact}"
                     data-image="${imageUrl}"
                     data-tags="${tags}">
              <img class="card-img" src="${imageUrl}" alt="${name}">
              <button class="edit-btn" data-type="destination">Edit</button>
              <h4 class="card-title">${name}</h4>
              <div class="card-content">
                <p class="card-desc">${description}</p>
                <span class="contact">📞 Contact Us: ${contact}</span>
              </div>
            </article>
        `;
        document.querySelector('#destinations-section .cards-grid').insertAdjacentHTML('beforeend', newCardHtml);

        const newlyAddedCard = document.querySelector(`.card[data-id="${newCardId}"]`);
        if (newlyAddedCard) {
            newlyAddedCard.querySelector('.edit-btn').addEventListener('click', (event) => {
                const card = event.target.closest('.card');
                const cardType = event.target.dataset.type;
                if (cardType === 'destination') {
                    hideForm(addHotelForm, hotelFormTitle, 'Add New Hotel');
                    destinationFormTitle.textContent = 'Edit Destination';
                    document.getElementById('destination-edit-id').value = card.dataset.id;
                    document.getElementById('destination-name').value = card.dataset.name;
                    document.getElementById('destination-contact').value = card.dataset.contact || '';
                    document.getElementById('destination-tags').value = card.dataset.tags || '';
                    document.getElementById('destination-description').value = card.dataset.description;
                    document.getElementById('destination-country').value = card.dataset.country;
                    document.getElementById('destination-season').value = card.dataset.season || '';

                    const currentImagePreview = document.getElementById('destination-current-image-preview');
                    const currentImage = document.getElementById('destination-current-image');
                    if (card.dataset.image) {
                        currentImage.src = card.dataset.image;
                        currentImagePreview.style.display = 'block';
                    } else {
                        currentImagePreview.style.display = 'none';
                    }
                    document.getElementById('destination-file-status').textContent = 'No new file selected.';

                    addDestinationForm.classList.remove('hidden');
                }
            });
        }
    }

    hideForm(form, destinationFormTitle, 'Add New Destination');
});

addHotelForm.addEventListener('submit', (event) => {
    event.preventDefault();

    const form = event.target;
    const id = form.querySelector('#hotel-edit-id').value;
    const name = form.querySelector('#hotel-name').value;
    const contact = form.querySelector('#hotel-contact').value;
    const destination = form.querySelector('#hotel-destination').value;
    const rating = form.querySelector('#hotel-rating').value;
    const minPrice = form.querySelector('#hotel-minprice').value;
    const maxPrice = form.querySelector('#hotel-maxprice').value;
    const description = form.querySelector('#hotel-description').value;
    const roomTypeInputs = form.querySelectorAll('#room-types-container input[name="roomType[]"]');
    const roomTypes = Array.from(roomTypeInputs).map(input => input.value.trim()).filter(value => value !== '').join(',');
    
    const amenitiesCheckboxes = form.querySelectorAll('#hotel-amenities input[type="checkbox"]:checked');
    const amenities = Array.from(amenitiesCheckboxes).map(cb => cb.value).join(',');
    const imageFile = form.querySelector('#hotel-image-upload').files[0];

    let imageUrl = '';
    const currentImageElement = document.getElementById('hotel-current-image');
    if (imageFile) {
        imageUrl = URL.createObjectURL(imageFile);
    } else if (currentImageElement && currentImageElement.src) {
        imageUrl = currentImageElement.src;
    } else {
        imageUrl = 'https://via.placeholder.com/400x240/cccccc/000000?text=No+Image';
    }


    if (id) {
        const cardToUpdate = document.querySelector(`.card[data-id="${id}"]`);
        if (cardToUpdate) {
            cardToUpdate.dataset.name = name;
            cardToUpdate.dataset.contact = contact;
            cardToUpdate.dataset.destination = destination;
            cardToUpdate.dataset.rating = rating;
            cardToUpdate.dataset.minprice = minPrice;
            cardToUpdate.dataset.maxprice = maxPrice;
            cardToUpdate.dataset.roomtypes = roomTypes;
            cardToUpdate.dataset.amenities = amenities;
            cardToUpdate.dataset.description = description;
            cardToUpdate.dataset.image = imageUrl;

            cardToUpdate.querySelector('.card-img').src = imageUrl;
            cardToUpdate.querySelector('.card-title').textContent = name;
            cardToUpdate.querySelector('.card-desc').textContent = description;
            cardToUpdate.querySelector('.contact').textContent = `📞 Contact Us: ${contact}`;
        }
    } else {
        const newCardId = `new-hot-${Date.now()}`;
        const newCardHtml = `
            <article class="card"
                     data-id="${newCardId}"
                     data-name="${name}"
                     data-destination="${destination}"
                     data-rating="${rating}"
                     data-minprice="${minPrice}"
                     data-maxprice="${maxPrice}"
                     data-roomtypes="${roomTypes}"
                     data-amenities="${amenities}"
                     data-description="${description}"
                     data-contact="${contact}"
                     data-image="${imageUrl}">
              <img class="card-img" src="${imageUrl}" alt="${name}">
              <button class="edit-btn" data-type="hotel">Edit</button>
              <h4 class="card-title">${name}</h4>
              <div class="card-content">
                <p class="card-desc">${description}</p>
                <span class="contact">📞 Contact Us: ${contact}</span>
              </div>
            </article>
        `;
        document.querySelector('#hotels-section .cards-grid').insertAdjacentHTML('beforeend', newCardHtml);

        const newlyAddedCard = document.querySelector(`.card[data-id="${newCardId}"]`);
        if (newlyAddedCard) {
            newlyAddedCard.querySelector('.edit-btn').addEventListener('click', (event) => {
                const card = event.target.closest('.card');
                const cardType = event.target.dataset.type;
                if (cardType === 'hotel') {
                    hideForm(addDestinationForm, destinationFormTitle, 'Add New Destination');
                    hotelFormTitle.textContent = 'Edit Hotel';
                    document.getElementById('hotel-edit-id').value = card.dataset.id;
                    document.getElementById('hotel-name').value = card.dataset.name;
                    document.getElementById('hotel-contact').value = card.dataset.contact || '';
                    document.getElementById('hotel-destination').value = card.dataset.destination;
                    document.getElementById('hotel-rating').value = card.dataset.rating;
                    document.getElementById('hotel-minprice').value = card.dataset.minprice;
                    document.getElementById('hotel-maxprice').value = card.dataset.maxprice;
                    document.getElementById('hotel-description').value = card.dataset.description;

                    while (roomTypesContainer.children.length > 0) {
                        roomTypesContainer.removeChild(roomTypesContainer.lastChild);
                    }
                    const roomTypesData = card.dataset.roomtypes ? card.dataset.roomtypes.split(',') : [];
                    if (roomTypesData.length > 0) {
                        roomTypesData.forEach(type => addRoomTypeInput(type.trim()));
                    } else {
                        addRoomTypeInput();
                    }
                    if (roomTypesContainer.children.length === 1) {
                        roomTypesContainer.querySelector('.remove-room-type-btn').classList.add('hidden');
                    } else {
                        Array.from(roomTypesContainer.children).forEach(child => {
                            const btn = child.querySelector('.remove-room-type-btn');
                            if (btn) btn.classList.remove('hidden');
                        });
                    }

                    const amenitiesCheckboxes = document.querySelectorAll('#hotel-amenities input[type="checkbox"]');
                    const cardAmenities = card.dataset.amenities ? card.dataset.amenities.split(',') : [];
                    amenitiesCheckboxes.forEach(checkbox => {
                        checkbox.checked = cardAmenities.includes(checkbox.value);
                    });

                    const currentImagePreview = document.getElementById('hotel-current-image-preview');
                    const currentImage = document.getElementById('hotel-current-image');
                    if (card.dataset.image) {
                        currentImage.src = card.dataset.image;
                        currentImagePreview.style.display = 'block';
                    } else {
                        currentImagePreview.style.display = 'none';
                    }
                    document.getElementById('hotel-file-status').textContent = 'No new file selected.';

                    addHotelForm.classList.remove('hidden');
                }
            });
        }
    }

    hideForm(form, hotelFormTitle, 'Add New Hotel');
});