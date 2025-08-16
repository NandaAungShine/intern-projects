    document.addEventListener('DOMContentLoaded', () => {
    
    const menuData = [
         { id: 1, name: "Cheeseburger", category: "foods", price: 5.99, image: "saleimg/Cheeseburger.jpg" },
        { id: 2, name: "Pepperoni Pizza", category: "foods", price: 12.99, image: "saleimg/Pepperoni-Pizza.jpg" },
        { id: 3, name: "French Fries", category: "snacks", price: 3.99, image: "saleimg/French-Fries.jpg" },
        { id: 4, name: "Cola", category: "drinks", price: 2.49, image: "saleimg/Cola.jpg" },
        { id: 5, name: "BBQ Ribs", category: "foods", price: 15.99, image: "saleimg/BBQ-Ribs.jpg" },
        { id: 6, name: "Caesar Salad", category: "foods", price: 8.99, image: "saleimg/Caesar-Salad.jpg" },
        { id: 7, name: "Chocolate Cake", category: "desserts", price: 6.99, image: "saleimg/Chocolate-Cake.jpg" },
        { id: 8, name: "Iced Tea", category: "drinks", price: 2.99, image: "saleimg/Iced-Tea.jpg" },
        { id: 9, name: "Onion Rings", category: "snacks", price: 4.49, image: "saleimg/Onion-Rings.jpg" },
        { id: 10, name: "Spaghetti Bolognese", category: "foods", price: 11.50, image: "saleimg/Spaghetti-Bolognese.jpg" },
        { id: 11, name: "Water", category: "drinks", price: 1.50, image: "saleimg/Water.jpg" },
        { id: 12, name: "Fruit Salad", category: "desserts", price: 5.75, image: "saleimg/Fruit-Salad.jpg" },
        { id: 13, name: "Nachos", category: "snacks", price: 7.25, image: "saleimg/Nachos.jpg" },
        { id: 14, name: "Lemonade", category: "drinks", price: 3.25, image: "saleimg/Lemonade.jpg" },
        { id: 15, name: "Grilled Chicken", category: "foods", price: 13.75, image: "saleimg/Grilled-Chicken.jpg" }
    ];

    let currentOrder = [];
    let currentTableNumber = 1;
    let discountPercentage = 0;

    const elements = {
        datetimeDisplay: document.getElementById('datetime'),
        menuItemsGrid: document.getElementById('menu-items-grid'),
        categoryTabs: document.querySelectorAll('.category-tab'),
        billItemsContainer: document.getElementById('bill-items'),
        subtotalAmount: document.getElementById('subtotal-amount'),
        discountPercentageInput: document.getElementById('discount-percentage'),
        discountAmountDisplay: document.getElementById('discount-amount'),
        totalAmountDisplay: document.getElementById('total-amount'),
        tableNumberInput: document.getElementById('table-number'),
        clearOrderBtn: document.getElementById('clear-order-btn'),
        checkoutBtn: document.getElementById('checkout-btn'),
        printBillBtn: document.getElementById('print-bill-btn'),
        paymentMethodSelect: document.getElementById('payment-method')
    };

    const utils = {
        formatCurrency: (amount) => `$${amount.toFixed(2)}`,
        updateDateTime: () => {
            const now = new Date();
            const options = {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            };
            elements.datetimeDisplay.textContent = now.toLocaleDateString('en-US', options);
        }
    };

    const menu = {
        renderItems: (category = 'all') => {
            elements.menuItemsGrid.innerHTML = '';
            const itemsToRender = category === 'all'
                ? menuData
                : menuData.filter(item => item.category === category);

            if (itemsToRender.length === 0) {
                elements.menuItemsGrid.innerHTML = '<p class="empty-message">No items found for this category.</p>';
                return;
            }

            itemsToRender.forEach(item => {
                const itemElement = document.createElement('div');
                itemElement.classList.add('menu-item');
                itemElement.innerHTML = `
                    <img src="${item.image}" alt="${item.name}">
                    <h3>${item.name}</h3>
                    <p>${utils.formatCurrency(item.price)}</p>
                    <button class="add-to-cart-btn" data-id="${item.id}">Add</button>
                `;
                elements.menuItemsGrid.appendChild(itemElement);
            });

            document.querySelectorAll('.add-to-cart-btn').forEach(button => {
                button.addEventListener('click', (event) => {
                    const itemId = parseInt(event.target.dataset.id);
                    const selectedItem = menuData.find(item => item.id === itemId);
                    if (selectedItem) {
                        order.addItem(selectedItem);
                    }
                });
            });
        },
        initCategoryTabs: () => {
            elements.categoryTabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    elements.categoryTabs.forEach(t => t.classList.remove('active'));
                    this.classList.add('active');
                    menu.renderItems(this.dataset.category);
                });
            });
        }
    };

    const order = {
        addItem: (item) => {
            const existingItemIndex = currentOrder.findIndex(orderItem => orderItem.id === item.id);

            if (existingItemIndex > -1) {
                currentOrder[existingItemIndex].quantity++;
            } else {
                currentOrder.push({ ...item, quantity: 1 });
            }
            order.renderBill();
        },
        updateItemQuantity: (id, change) => {
            const itemIndex = currentOrder.findIndex(item => item.id === id);
            if (itemIndex > -1) {
                currentOrder[itemIndex].quantity += change;
                if (currentOrder[itemIndex].quantity <= 0) {
                    currentOrder.splice(itemIndex, 1);
                }
                order.renderBill();
            }
        },
        removeItem: (id) => {
            currentOrder = currentOrder.filter(item => item.id !== id);
            order.renderBill();
        },
        clearOrder: () => {
            if (confirm('Are you sure you want to clear the entire order?')) {
                currentOrder = [];
                order.renderBill();
                elements.tableNumberInput.value = 1;
                elements.discountPercentageInput.value = 0;
                discountPercentage = 0; 
            }
        },
        calculateTotals: () => {
            const subtotal = currentOrder.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            const discountAmount = subtotal * (discountPercentage / 100);
            const total = subtotal - discountAmount;
            return { subtotal, discountAmount, total };
        },
        renderBill: () => {
            elements.billItemsContainer.innerHTML = '';
            if (currentOrder.length === 0) {
                elements.billItemsContainer.innerHTML = '<div class="empty-bill-message">No items added yet.</div>';
            } else {
                currentOrder.forEach(item => {
                    const itemTotalPrice = item.price * item.quantity;
                    const billItemElement = document.createElement('div');
                    billItemElement.classList.add('bill-item');
                    billItemElement.innerHTML = `
                        <div class="bill-item-details">
                            <span class="item-name">${item.name}</span>
                            <span class="item-price-per-unit">${utils.formatCurrency(item.price)} per unit</span>
                        </div>
                        <div class="bill-item-controls">
                            <button class="quantity-btn minus-btn" data-id="${item.id}">-</button>
                            <span class="item-quantity-display">${item.quantity}</span>
                            <button class="quantity-btn plus-btn" data-id="${item.id}">+</button>
                            <span class="item-total-price">${utils.formatCurrency(itemTotalPrice)}</span>
                            <button class="remove-item-btn" data-id="${item.id}">×</button>
                        </div>
                    `;
                    elements.billItemsContainer.appendChild(billItemElement);
                });

               
                elements.billItemsContainer.querySelectorAll('.minus-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => order.updateItemQuantity(parseInt(e.target.dataset.id), -1));
                });
                elements.billItemsContainer.querySelectorAll('.plus-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => order.updateItemQuantity(parseInt(e.target.dataset.id), 1));
                });
                elements.billItemsContainer.querySelectorAll('.remove-item-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => order.removeItem(parseInt(e.target.dataset.id)));
                });
            }

            const { subtotal, discountAmount, total } = order.calculateTotals();
            elements.subtotalAmount.textContent = utils.formatCurrency(subtotal);
            elements.discountAmountDisplay.textContent = utils.formatCurrency(discountAmount);
            elements.totalAmountDisplay.textContent = utils.formatCurrency(total);
        },
        checkout: () => {
            if (currentOrder.length === 0) {
                alert('Please add items to the order before checking out.');
                return;
            }

            currentTableNumber = parseInt(elements.tableNumberInput.value) || 1;
            const selectedPaymentMethod = elements.paymentMethodSelect.value;

            if (!selectedPaymentMethod) {
                alert('Please select a payment method.');
                return;
            }

            const { total } = order.calculateTotals();

            let checkoutSummary = `--- Order Summary ---\n`;
            checkoutSummary += `Table Number: ${currentTableNumber}\n`;
            checkoutSummary += `Customer Name: (Not implemented in this version)\n\n`; 
            checkoutSummary += `Items:\n`;
            currentOrder.forEach(item => {
                checkoutSummary += `- ${item.name} x ${item.quantity} (${utils.formatCurrency(item.price * item.quantity)})\n`;
            });
            checkoutSummary += `\nSubtotal: ${elements.subtotalAmount.textContent}\n`;
            checkoutSummary += `Discount (${discountPercentage}%): ${elements.discountAmountDisplay.textContent}\n`;
            checkoutSummary += `Total: ${elements.totalAmountDisplay.textContent}\n`;
            checkoutSummary += `Payment Method: ${selectedPaymentMethod}\n`;
            checkoutSummary += `---------------------\n`;
            checkoutSummary += `Thank you for your order!`;

            alert(checkoutSummary); 
            console.log(checkoutSummary); 

            

            order.clearOrder();
        },
        printBill: () => {
            if (currentOrder.length === 0) {
                alert('There are no items to print on the bill.');
                return;
            }
            alert('Printing bill (This would typically open a print dialog or send to a printer).');
            
            window.print(); 
        }
    };

   
    const init = () => {
       
        utils.updateDateTime();
        setInterval(utils.updateDateTime, 60000); 

        
        menu.initCategoryTabs();
        menu.renderItems('all');

       
        elements.discountPercentageInput.addEventListener('input', (event) => {
            const value = parseInt(event.target.value);
            if (isNaN(value) || value < 0 || value > 100) {
                discountPercentage = 0;
                event.target.value = 0;
                alert('Discount percentage must be between 0 and 100.');
            } else {
                discountPercentage = value;
            }
            order.renderBill(); 
        });

       
        elements.clearOrderBtn.addEventListener('click', order.clearOrder);
        elements.checkoutBtn.addEventListener('click', order.checkout);
        elements.printBillBtn.addEventListener('click', order.printBill);

        
        order.renderBill();
    };

    init();
});