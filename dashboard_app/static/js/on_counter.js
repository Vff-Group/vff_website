var searchInput = $("#searchInput");
var subCategoryTable = $("#subCategoryTable");
var subCategoryRows = subCategoryTable.find("tr");

// Add an event listener to the search input
searchInput.on("input", function () {
  var query = searchInput.val().toLowerCase();
  console.log("query::" + query);
  // Iterate through the table rows and hide/show based on the query
  subCategoryRows.each(function () {
    var subCategoryName = $(this).find("h6.mb-0").text().toLowerCase();
    console.log("subCategoryName::" + subCategoryName);
    if (subCategoryName.includes(query)) {
      $(this).show();
    } else {
      $(this).hide();
    }
  });
});

$(document).on("click", ".increment", function () {
  var input = $(this).closest("tr").find("input[type='number']");
  input.val(parseInt(input.val()) + 1);
});

$(document).on("click", ".decrement", function () {
  var input = $(this).closest("tr").find("input[type='number']");
  var newValue = parseInt(input.val()) - 1;
  if (newValue >= 1) {
    input.val(newValue);
  }
});


//MOdal Class is triggered to show Add Ons
$(document).ready(function () {
  var selectedItems = {}; // Object to keep track of selected items and their prices

  // Attach an event listener to the modal when it is shown
  $("#modal-default1").on("show.bs.modal", function () {
    const dictMap = {
      booking_id: generated_booking_id,
    };
    const csrfToken = getCSRFToken();
    $.ajax({
      type: "POST",
      url: "/admin_dashboard/load_extra_items/",
      data: JSON.stringify(dictMap),
      headers: {
        "X-CSRFToken": csrfToken, // Include the CSRF token in the headers
      },
      contentType: "application/json",
      success: function (data) {
        var grossTotal = 0; // Total amount
        var addOnsTotal = 0;
        var deliveryTotal = 0;
        var discountAmount = 0;
        var discountedAmount = 0;
        var delivery_price = 0;
        var delivery_range = 0;
        var delivery_charges = 0;

        if (!isNaN(addOnsTotal)) {
          $("#addons-total").text("Rs." + addOnsTotal + "/-");
        }
        // Handle the data you received from the server
        console.log("datata:" + JSON.stringify(data));
        //Gets Extra Items Details
        var extra_items_data = data.extra_items_data;
        //TOtal Cost and Quantity
        var sum_data = data.sum_data;
        var delivery_data = data.delivery_charges_data;

        grossTotal = sum_data[0].total_cost;
        delivery_price = delivery_data[0].delivery_price;
        delivery_range = delivery_data[0].delivery_range;

        var subTotal = grossTotal;
        $("#sub-total").text("Rs." + subTotal + "/-");
        $("#gross-total").text("Rs." + grossTotal + "/-");
        grossQuantity = sum_data[0].total_quantity;

        console.log("grossTotalDB::" + grossTotal);

        //To Create delivery charges checkbox
        // Function to create a checkbox element for the delivery charge
        function createDeliveryCheckbox(charge) {
          var checkboxId = "delivery-" + charge.dcharge_id;
          var checkboxLabel =
            "Delivery Charge - Rs." + charge.delivery_price + "/-";

          var divider = $("<hr />");
          var checkboxContainer = $("<div class='form-check'></div>");
          var checkbox = $(
            "<input class='form-check-input' type='checkbox' id='" +
              checkboxId +
              "' data-delivery-price='" +
              charge.delivery_price +
              "'>"
          );
          var label = $(
            "<label class='form-check-label' for='" +
              checkboxId +
              "'>" +
              checkboxLabel +
              "</label>"
          );

          // Attach an event handler to update grossTotal when the checkbox state changes
          checkState = false;
          checkbox.on("change", function () {
            if (checkbox.is(":checked")) {
              console.log("checked no");
              if (discountedAmount !== 0 && !isNaN(discountedAmount)) {
                console.log("Add BdiscountedAmount---->" + discountedAmount);
                delivery_charges = charge.delivery_price;
                var sum = (discountedAmount += charge.delivery_price).toFixed(
                  2
                );
                discountedAmount = sum;
                $("#gross-total").text("Rs." + discountedAmount + "/-");
                $("#delivery-charges").text("Rs." + delivery_charges + "/-");
                checkState = true;
              } else if (!isNaN(grossTotal)) {
                console.log("Add BgrossTotal---->" + grossTotal);
                console.log(
                  "charge.delivery_price===>" + charge.delivery_price
                );
                var sum = (grossTotal += charge.delivery_price).toFixed(2);
                console.log("sumss::" + sum);
                delivery_charges = charge.delivery_price;
                grossTotal = sum;
                console.log("Add AgrossTotal---->" + grossTotal);
                $("#gross-total").text("Rs." + grossTotal + "/-");
                $("#delivery-charges").text("Rs." + delivery_charges + "/-");
                checkState = true;
              }
            } else {
              console.log("checked off");
              if (checkState === true) {
                if (discountedAmount !== 0 && !isNaN(discountedAmount)) {
                  delivery_charges = 0;
                  delivery_charges = charge.delivery_price;

                  var sum = (discountedAmount -= charge.delivery_price).toFixed(
                    2
                  );
                  discountedAmount = sum;
                  $("#gross-total").text("Rs." + discountedAmount + "/-");
                  $("#delivery-charges").text("Rs." + delivery_charges + "/-");
                  checkState = false;
                } else if (!isNaN(grossTotal)) {
                  var sum = (grossTotal -= charge.delivery_price);

                  delivery_charges = 0;

                  grossTotal = sum;

                  $("#gross-total").text("Rs." + grossTotal + "/-");
                  $("#delivery-charges").text("Rs." + delivery_charges + "/-");
                  checkState = false;
                }
              }
            }

            // Update the grossTotal display (if you have a display element)
            // For example: $('#grossTotal').text(grossTotal);
          });
          checkboxContainer.append(divider);
          checkboxContainer.append(checkbox);
          checkboxContainer.append(label);
          console.log("checkboxContainer::" + checkboxContainer);
          return checkboxContainer;
        }

        // Function to add the delivery charge checkbox to the container
        function addDeliveryChargeCheckbox() {
          var deliveryChargesContainer = $("#delivery-charges-container");
          console.log("delivery_range::" + delivery_range);
          console.log("delivery_price::" + delivery_price);

          if (grossTotal < delivery_range) {
            // Only add the delivery charge checkbox if gross total is below Rs 500
            var charge = delivery_data[0];
            var checkbox = createDeliveryCheckbox(charge);
            deliveryChargesContainer.empty();

            deliveryChargesContainer.append(checkbox);

            //UPDATE GROSS_TOTAL
            // Update grossTotal here as well

            // Add a label for the delivery charges condition
            var conditionLabel = $(
              "<div class='container mt-2'><p class='text-muted'>Delivery charges are applicable only if the gross total is below Rs " +
                delivery_range +
                ".</p></div>"
            );
            deliveryChargesContainer.append(conditionLabel);
          } else {
            // Remove the container if the gross total is above the delivery range
            deliveryChargesContainer.remove();
          }
        }

        // Call the function to add the delivery charge checkbox to the container
        addDeliveryChargeCheckbox();

        //Add Ons CheckBoxes
        var checkboxesHTML = "";
        extra_items_data.forEach(function (item) {
          checkboxesHTML += '<div class="form-check">';
          checkboxesHTML +=
            '<label class="form-check-label" for="checkbox-' +
            item.extra_item_id +
            '">' +
            item.extra_item_name +
            " [Rs." +
            item.price +
            "/-]</label>";
          checkboxesHTML +=
            '<input class="form-check-input" type="checkbox" id="checkbox-' +
            item.extra_item_id +
            '" data-item-id="' +
            item.extra_item_id +
            '" data-item-name="' +
            item.extra_item_name +
            '" " data-item-price="' +
            item.price +
            '">';
          checkboxesHTML += "</div>";
        });
        $("#checkboxes").html(checkboxesHTML);

        // Attach an event listener to the checkboxes
        $("input[data-item-id]").change(function () {
          console.log("triggering here also");
          var itemId = $(this).data("item-id");
          var itemPrice = parseFloat($(this).data("item-price"));
          var itemName = parseFloat($(this).data("item-name"));
          console.log("itemPrice::" + itemPrice);
          if (this.checked) {
            // Checkbox is checked
            selectedItems[itemId] = itemPrice;
            grossTotal += itemPrice;
            addOnsTotal += itemPrice;
          } else {
            // Checkbox is unchecked
            delete selectedItems[itemId];
            grossTotal -= itemPrice;
            addOnsTotal -= itemPrice;
          }
          console.log("addOnsTotal::" + addOnsTotal);
          // Update the gross total amount

          if (discountedAmount !== 0 && !isNaN(discountedAmount)) {
            $("#gross-total").text("Rs." + discountedAmount + "/-");
          } else {
            $("#gross-total").text("Rs." + grossTotal + "/-");
          }
          if (!isNaN(addOnsTotal)) {
            $("#addons-total").text("Rs." + addOnsTotal + "/-");
          }

          // Update the discounted amount
          if (!isNaN(discountAmount)) {
            $("#discount-amount").text("Rs." + discountAmount + "/-");
          }
        });

        // Attach an event listener to the discount input
        $("#discounted-input").on("input", function () {
          discount = parseFloat($(this).val());

          // Calculate the discounted amount
          discountedAmount = grossTotal - grossTotal * (discount / 100);

          discountAmount = grossTotal * (discount / 100);
          discountAmount = discountAmount.toFixed(2);

          console.log("discountAmount::" + grossTotal * (discount / 100));
          // Update the discounted amount
          discountedAmount = discountedAmount.toFixed(2);
          if (discount === "" || isNaN(discount)) {
            discountAmount = 0;
            $("#discount-amount").text("Rs." + discountAmount + "/-");
          }
          if (!isNaN(discountAmount)) {
            $("#discount-amount").text("Rs." + discountAmount + "/-");
          }

          if (discountedAmount !== 0 && !isNaN(discountedAmount)) {
            $("#gross-total").text("Rs." + discountedAmount + "/-");
          } else {
            $("#gross-total").text("Rs." + grossTotal + "/-");
          }
        });

        if (discountedAmount !== 0 && !isNaN(discountedAmount)) {
          $("#gross-total").text("Rs." + discountedAmount + "/-");
        } else {
          $("#gross-total").text("Rs." + grossTotal + "/-");
        }
        var totalPayment = 0;
        if (discountedAmount !== 0 && !isNaN(discountedAmount)) {
          totalPayment = discountedAmount;
        } else {
          totalPayment = grossTotal;
        }
        //Payment Start
        var options = {
          key: "rzp_live_SeGnLgb5JnY8Id", // Enter the Key ID generated from the Dashboard
          amount: totalPayment * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
          currency: "INR",
          name: "VFF Group", //your business name
          description: "Laundry Service Charges",
          image: "https://vff-group.com/static/images/logo.png",
          handler: function (response) {
            alert(response.razorpay_payment_id);
            //alert(response.razorpay_order_id);
            //alert(response.razorpay_signature)
          },
          prefill: {
            //We recommend using the prefill parameter to auto-fill customer's contact information, especially their phone number
            name: "Shaheed Maniyar", //your customer's name
            email: "shahidmaniyar888@gmail.com",
            contact: "8296565587", //Provide the customer's phone number for better conversion rates
          },
          notes: {
            address: "Tilakwadi",
          },
          theme: {
            color: "#3399cc",
          },
        };
        var rzp1 = new Razorpay(options);
        rzp1.on("payment.failed", function (response) {
          alert(response.error.code);
          alert(response.error.description);
          alert(response.error.source);
          alert(response.error.step);
          alert(response.error.reason);
          // alert(response.error.metadata.order_id);
          alert(response.error.metadata.payment_id);
        });
        document.getElementById("pay-button").onclick = function (e) {
          rzp1.open();
          e.preventDefault();
        };
        //Payment End
      },
      error: function (error) {
        console.error("Error:", error);
      },
    });
  });
});

function payment_show(totalPayment) {
  var options = {
    key: "rzp_test_qtHIWapeUEAAZO", // Enter the Key ID generated from the Dashboard
    amount: totalPayment * 100, // Amount is in currency subunits. Default currency is INR. Hence, 50000 refers to 50000 paise
    currency: "INR",
    name: "VFF Group", //your business name
    description: "Laundry Service Charges",
    image: "https://vff-group.com/static/images/logo.png",
    handler: function (response) {
      alert(response.razorpay_payment_id);
      //alert(response.razorpay_order_id);
      //alert(response.razorpay_signature)
    },
    prefill: {
      //We recommend using the prefill parameter to auto-fill customer's contact information, especially their phone number
      name: "Shaheed Maniyar", //your customer's name
      email: "shahidmaniyar888@gmail.com",
      contact: "8296565587", //Provide the customer's phone number for better conversion rates
    },
    notes: {
      address: "Tilakwadi",
    },
    theme: {
      color: "#3399cc",
    },
  };
  var rzp1 = new Razorpay(options);
  rzp1.on("payment.failed", function (response) {
    alert(response.error.code);
    alert(response.error.description);
    alert(response.error.source);
    alert(response.error.step);
    alert(response.error.reason);
    // alert(response.error.metadata.order_id);
    alert(response.error.metadata.payment_id);
  });
  document.getElementById("pay-button").onclick = function (e) {
    rzp1.open();
    e.preventDefault();
  };
}

// Get the CSRF token from the cookie
function getCSRFToken() {
  const cookies = document.cookie.split(";");
  for (let i = 0; i < cookies.length; i++) {
    const cookie = cookies[i].trim();
    if (cookie.startsWith("csrftoken=")) {
      return cookie.substring("csrftoken=".length, cookie.length);
    }
  }
  return null;
}

var selectedItems = [];
let selectedCategoryId = null;
let selectedCategoryName = null;
let selectedCategoryImage = null;
let selectedCategoryBookingID = null;
let generated_booking_id = "";

//Create booking ID Before adding items to cart
$("#generate-booking-id").on("click", function () {
  var selected_customer_id = document.getElementById("selected-customer-id");
  var customer_name_input = document.getElementById("customer-name");

  var customer_id = selected_customer_id.value.trim();
  var customer_name = customer_name_input.value.trim();

  if (customer_id === "") {
    showToast("Alert", "Please Search customer before adding any items");
    return;
  }
  const dictMap = {
    customer_id: customer_id,
  };
  const csrfToken = getCSRFToken();
  $.ajax({
    type: "POST",
    url: "/admin_dashboard/generate_booking_id/", // Adjust the URL as needed
    data: JSON.stringify(dictMap),
    headers: {
      "X-CSRFToken": csrfToken, // Include the CSRF token in the headers
    },
    contentType: "application/json",
    success: function (response) {
      console.log(response.message);
      // Handle success response
      const bookingIDData = response.booking_id;
      // Now you can access the cartItemsData as a JavaScript object
      // console.log(bookingIDData);
      //TODO:Need to save the booking ID

      var booking_id_input = document.getElementById("selected-booking-id");
      booking_id_input.value = bookingIDData; // Set the value in the hidden input
      generated_booking_id = bookingIDData;
      $("#generate-booking-id").text("Booking ID: " + bookingIDData); // Update the button text
    },
    error: function (error) {
      console.error(error.responseJSON.message);
      // Handle error response
    },
  });
});

//Add To Cart Button
$("#add_to_cart").on("click", function () {
  // Get the selected values for Category, Service Type, and Sub Section
  var selectedCategory = $("#input-category").val();
  var selectedServiceType = $("#input-price").val();
  var selectedSubSection = $("#input-section").val();

  var inputElement = document.getElementById("item-quantity");

  //customer-name,selected-customer-id,selected-mobile-no,selected-customer-name
  var selected_customer_id = document.getElementById("selected-customer-id");
  var customer_name_input = document.getElementById("customer-name");
  var booking_id_input = document.getElementById("selected-booking-id");

  var customer_id = selected_customer_id.value.trim();
  var customer_name = customer_name_input.value.trim();
  var booking_id = booking_id_input.value.trim();

  if (customer_id === "") {
    showToast("Alert", "Please Search customer before adding any items");
    return;
  }

  if (booking_id === "") {
    showToast(
      "Alert",
      "Please generate Booking ID Before adding any items to cart"
    );
    return;
  }

  var kgs_quantity = inputElement.value.trim();

  // Perform validation
  if (!selectedCategory) {
    // Show a toast message for validation failure
    showToast("Validation Error", "Please Select Category");
    return; // Stop further execution
  }

  // Perform validation
  if (!selectedServiceType && selectedCategory !== "DRY CLEAN") {
    // Show a toast message for validation failure
    showToast("Validation Error", "Please Price Type");
    return; // Stop further execution
  }

  // Perform validation
  if (!selectedSubSection && selectedCategory === "DRY CLEAN") {
    // Show a toast message for validation failure
    showToast("Validation Error", "Sub Section.");
    return; // Stop further execution
  }

  const dictMap = {};

  //TO Check if Quantity is added or not
  if (selectedCategory !== "DRY CLEAN") {
    if (kgs_quantity === "") {
      inputElement.classList.remove("is-valid");
      inputElement.classList.add("is-invalid");
      showToast("Alert", "Please Provide the quantity in Kgs");
      return;
    } else if (kgs_quantity !== "" && kgs_quantity < 5) {
      inputElement.classList.remove("is-valid");
      inputElement.classList.add("is-invalid");
      showToast("Alert", "We accept only order above 5 Kgs");
      return;
    } else {
      inputElement.classList.remove("is-invalid");
      inputElement.classList.add("is-valid");
    }
  }

  // console.log('SelectedCategory::'+selectedCategory);
  //console.log('selectedSubSection::'+selectedSubSection);
  //console.log('selectedServiceType::'+selectedServiceType);

  jsonItems = JSON.stringify(selectedItems);
  if (selectedItems.length === 0) {
    showToast("Alert", "Please select the laundry items before adding to cart");
    return;
  }

  if (selectedCategory !== "DRY CLEAN") {
    const subCategoryNameList = selectedItems.map(
      (item) => `${item.sub_cat_name} (${item.item_quantity})`
    );
    const subCategoryIDList = selectedItems.map((item) => `${item.sub_cat_id}`);
    const subCategoryImageList = selectedItems.map(
      (item) => `${item.sub_cat_img}`
    );

    // console.log('subCategoryNameList::'+subCategoryNameList);
    //console.log('subCategoryIDList::'+subCategoryIDList);
    //console.log('subCategoryImageList::'+subCategoryImageList);
    //console.log('customer_id::'+customer_id);

    var subCategoryNames = makeCommaSeparatedList(subCategoryNameList);
    var subCategoryID = makeCommaSeparatedList(subCategoryIDList);
    var subCategoryImage = makeCommaSeparatedList(subCategoryImageList);

    // console.log("Item Details::"+jsonItems)
    var totalCost = 0.0;
    var actualCost = 0.0;
    var regular_price = get_prize(selectedServiceType);
    //console.log('regular_price::'+regular_price);
    var express_price = get_prize(selectedServiceType);
    var offer_price = get_prize(selectedServiceType);
    if (selectedServiceType.toLowerCase().includes("Regular")) {
      totalCost = parseFloat(regular_price) * parseFloat(kgs_quantity);
      actualCost = parseFloat(regular_price);
    } else if (selectedServiceType.toLowerCase().includes("Express")) {
      totalCost = parseFloat(express_price) * parseFloat(kgs_quantity);
      actualCost = parseFloat(express_price);
    } else {
      totalCost = parseFloat(offer_price) * parseFloat(kgs_quantity);
      actualCost = parseFloat(offer_price);
    }

    dictMap["cat_id"] = selectedCategoryId;
    dictMap["customer_id"] = customer_id;
    dictMap["booking_id"] = booking_id;
    dictMap["key"] = 2;
    dictMap["booking_type"] = selectedServiceType;
    dictMap["cat_img"] = selectedCategoryImage;
    dictMap["cat_name"] = selectedCategoryName;

    dictMap["sub_cat_name"] = subCategoryNames;
    dictMap["item_quantity"] = kgs_quantity;
    dictMap["actual_cost"] = actualCost;
    dictMap["cost"] = totalCost;
    dictMap["type_of"] = "Kgs"; //Kgs
    dictMap["sub_cat_id"] = subCategoryID;
    dictMap["sub_cat_img"] = subCategoryImage;
    dictMap["section_type"] = "All";

    //console.log('ActualCost::'+actualCost);
    //console.log('TotalCost::'+totalCost);
  }
  //End of Other Laundry Services Add Item to Cart
  else {
    dictMap["cat_id"] = selectedCategoryId;
    dictMap["booking_id"] = booking_id;
    dictMap["customer_id"] = customer_id;
    dictMap["booking_type"] = "Dry Cleaning";
    dictMap["cat_img"] = selectedCategoryImage;
    dictMap["cat_name"] = selectedCategoryName;
    dictMap["key"] = 1;
    dictMap["all_items"] = selectedItems;
  }

  // Get the CSRF token
  const csrfToken = getCSRFToken();
  $.ajax({
    type: "POST",
    url: "/admin_dashboard/add_items_to_cart/", // Adjust the URL as needed
    data: JSON.stringify(dictMap),
    headers: {
      "X-CSRFToken": csrfToken, // Include the CSRF token in the headers
    },
    contentType: "application/json",
    success: function (response) {
      //Empty the cart items
      selectedItems = [];
      $("#subCategoryTable .quantity").text("0");

      console.log(response.message);
      // Handle success response
      const cartItemsData = response.cart_items_data;
      // Now you can access the cartItemsData as a JavaScript object
      console.log(cartItemsData);
      // Function to populate the table with data
      function populateCartItemsTable(data) {
        const cartItemsTable = $("#cartItemsTable tbody");
        cartItemsTable.empty(); // Clear existing data in the table

        data.forEach(function (item) {
          const row = $("<tr>");
          var type = item.type;
          var itemName = "",
            itemImage = "",
            itemsName = "";

          if (type === "Kgs") {
            itemName = item.cat_name;
            itemImage = item.cat_img;
            itemsName = item.sub_cat_name;
          } else {
            itemName = item.sub_cat_name;
            itemImage = item.sub_cat_img;
            itemsName = item.section_type;
          }

          row.append(
            "<td><div class='d-flex px-2 py-1'> <div class='d-flex px-2 py-1'><img src=" +
              itemImage +
              " class='avatar avatar-sm me-3' alt='user1'> </div> <div class='d-flex flex-column justify-content-center'> <h6 class='mb-0 text-sm' id='sub_cat_name'>" +
              itemName +
              "</h6> <p class='text-xs text-secondary mb-0'>[" +
              itemsName +
              "]</p> </div></div> </div> </td>"
          );
          row.append(
            "<td><p class='text-xs text-secondary mb-0'>" +
              item.booking_type +
              "</p></td>"
          );
          row.append(
            "<td><p class='text-xs text-secondary mb-0'> Rs." +
              item.item_cost +
              "/-</p></td>"
          );
          row.append(
            "<td><p class='text-xs text-secondary mb-0'> " +
              item.item_quantity +
              " " +
              item.type +
              "</p></td>"
          );

          // Add a delete icon and attach a click event to trigger the delete
          const deleteIcon = $(
            "<td><i class='fas fa-trash-alt delete-icon' data-item-id='" +
              item.itemid +
              "'></i></td>"
          );
          row.append(deleteIcon);

          cartItemsTable.append(row);
        });

        // Add a click event handler for the delete icons
        $(".delete-icon").click(function () {
          const itemId = $(this).data("item-id");
          // Perform the delete operation using AJAX, passing itemId to your delete API endpoint.
          // You can use the itemId to identify the item you want to delete.
          // Make an AJAX call to delete the item and then refresh the table.
          deleteCartItem(itemId, customer_id, booking_id);
        });
      }

      populateCartItemsTable(cartItemsData);
    },
    error: function (error) {
      console.error(error.responseJSON.message);
      // Handle error response
    },
  });
});

// Function to delete a cart item using AJAX
function deleteCartItem(itemId, customer_id, booking_id) {
  const csrfToken = getCSRFToken();

  const dictMap = {
    item_id: itemId,
  };
  $.ajax({
    type: "POST",
    url: "/admin_dashboard/delete_cart_item/", // Adjust the URL as needed
    data: JSON.stringify(dictMap),
    headers: {
      "X-CSRFToken": csrfToken,
    },
    contentType: "application/json",
    success: function (response) {
      console.log(response.message);
      // Handle success response
      // After successfully deleting the item, you can refresh the table
      // to reflect the updated data.
      // Reload your data and call populateCartItemsTable() again.
      reloadCartItem(itemId, customer_id, booking_id);
    },
    error: function (error) {
      console.error(error.responseJSON.message);
      // Handle error response
    },
  });
}

function reloadCartItem(itemId, customer_id, booking_id) {
  const csrfToken = getCSRFToken();
  const dictMap = {
    customer_id: customer_id,
    booking_id: booking_id,
  };
  $.ajax({
    type: "POST",
    url: "/admin_dashboard/load_cart_items_after_deletion/",

    data: JSON.stringify(dictMap),
    headers: {
      "X-CSRFToken": csrfToken, // Include the CSRF token in the headers
    },
    contentType: "application/json",
    success: function (response) {
      console.log(response.message);
      // Handle success response
      const cartItemsData = response.cart_items_data;
      // Now you can access the cartItemsData as a JavaScript object
      console.log(cartItemsData);
      // Function to populate the table with data
      function populateCartItemsTable(data) {
        const cartItemsTable = $("#cartItemsTable tbody");
        cartItemsTable.empty(); // Clear existing data in the table

        data.forEach(function (item) {
          const row = $("<tr>");
          var type = item.type;
          var itemName = "",
            itemImage = "",
            itemsName = "";

          if (type === "Kgs") {
            itemName = item.cat_name;
            itemImage = item.cat_img;
            itemsName = item.sub_cat_name;
          } else {
            itemName = item.sub_cat_name;
            itemImage = item.sub_cat_img;
            itemsName = item.section_type;
          }
          row.append(
            "<td><div class='d-flex px-2 py-1'> <div class='d-flex px-2 py-1'><img src=" +
              itemImage +
              " class='avatar avatar-sm me-3' alt='user1'> </div> <div class='d-flex flex-column justify-content-center'> <h6 class='mb-0 text-sm' id='sub_cat_name'>" +
              itemName +
              "</h6> <p class='text-xs text-secondary mb-0'>[" +
              itemsName +
              "]</p> </div></div> </div> </td>"
          );
          row.append(
            "<td><p class='text-xs text-secondary mb-0'>" +
              item.booking_type +
              "</p></td>"
          );
          row.append(
            "<td><p class='text-xs text-secondary mb-0'> Rs." +
              item.item_cost +
              "/-</p></td>"
          );
          row.append(
            "<td><p class='text-xs text-secondary mb-0'> " +
              item.item_quantity +
              " " +
              item.type +
              "</p></td>"
          );

          // Add a delete icon and attach a click event to trigger the delete
          const deleteIcon = $(
            "<td><i class='fas fa-trash-alt delete-icon' data-item-id='" +
              item.itemid +
              "'></i></td>"
          );
          row.append(deleteIcon);

          cartItemsTable.append(row);
        });
        //cart-sub-total

        // Add a click event handler for the delete icons
        $(".delete-icon").click(function () {
          const itemId = $(this).data("item-id");
          // Perform the delete operation using AJAX, passing itemId to your delete API endpoint.
          // You can use the itemId to identify the item you want to delete.
          // Make an AJAX call to delete the item and then refresh the table.
          deleteCartItem(itemId, customer_id, booking_id);
        });
      }

      populateCartItemsTable(cartItemsData);
    },
    error: function (error) {
      console.error(error.responseJSON.message);
      // Handle error response
    },
  });
}

function get_prize(inputString) {
  const parts = inputString.split(" ");
  if (parts.length >= 3) {
    const valueAtIndex2 = parts[2];
    console.log(valueAtIndex2); // Output: "125"
    return valueAtIndex2;
  } else {
    console.log("Not enough parts in the input string.");
  }
  return 0;
}

function makeCommaSeparatedList(subCategoryNameList) {
  return subCategoryNameList.join(", ");
}

$("#subCategoryTable").on("click", ".increment, .decrement", function () {
  var row = $(this).closest("tr");
  var sub_cat_name = $(this).closest("tr").find("#sub_cat_name").text();
  var subcatid = $(this).closest("tr").find("#sub_catid").text();
  var sub_cat_img = $(this).closest("tr").find("#sub_cat_img").text();
  var actual_cost = $(this).closest("tr").find("#cost").text();
  var type = $(this).closest("tr").find("#type").text();
  var cat_name = $(this).closest("tr").find("#cat_name").text();

  var quantityInput = row.find(".quantity");
  var currentQuantity = parseInt(quantityInput.text());

  var total_cost = 0.0;
  // Find the existing item in the selectedItems list with the same subcatid
  var selectedItemIndex = selectedItems.findIndex(
    (item) => item.subcatid === subcatid
  );

  if ($(this).hasClass("increment")) {
    // Handle increment logic
    quantityInput.text(currentQuantity + 1);

    if (selectedItemIndex !== -1) {
      // Update the quantity in the selected item
      total_cost = parseFloat(actual_cost) * (parseFloat(currentQuantity) + 1);
      console.log("total_cost_added::" + total_cost);
      selectedItems[selectedItemIndex].item_quantity = currentQuantity + 1;
      selectedItems[selectedItemIndex].cost = total_cost;
    } else {
      // Create a new object and push it to the list
      section_type_selected = "All";
      if (selectedCategoryName == "DRY CLEAN") {
        var section_type = $(this).closest("tr").find("#section_type").text();
        section_type_selected = section_type;
      }
      total_cost = parseFloat(actual_cost) * (parseFloat(currentQuantity) + 1);
      var newItem = {
        sub_cat_name: sub_cat_name,
        subcatid: subcatid,
        item_quantity: currentQuantity + 1,
        actual_cost: actual_cost,
        cost: total_cost,
        type_of: type,
        sub_cat_id: subcatid,
        sub_cat_img: sub_cat_img,
        section_type: section_type_selected,
      };
      /* var newItem = {
            subCategoryName: sub_cat_name,
            item_quantity: currentQuantity + 1,
            sub_cat_name: sub_cat_name,
            actual_cost: 45, // Replace 'item.cost' with the actual value
            cost: 45 * (currentQuantity + 1),
            type_of: 'Kgs', // Replace 'item.typeOf' with the actual value
            sub_cat_id: subcatid,
            sub_cat_img: 'NA', // Replace 'item.subCategoryImage' with the actual value
            section_type: 'All'
        };*/
      selectedItems.push(newItem);
    }
  } else if ($(this).hasClass("decrement") && currentQuantity > 0) {
    // Handle decrement logic
    quantityInput.text(currentQuantity - 1);

    if (selectedItemIndex !== -1) {
      // Update the quantity in the selected item
      selectedItems[selectedItemIndex].item_quantity = currentQuantity - 1;
      //selectedItems[selectedItemIndex].item_quantity = currentQuantity - 1;
      //selectedItems[selectedItemIndex].cost = selectedItems[selectedItemIndex].actual_cost * (currentQuantity - 1);
      // Remove the item from the list if the quantity is 0
      if (currentQuantity - 1 === 0) {
        selectedItems.splice(selectedItemIndex, 1);
      }
    }
  }

  // Remove the item from the JSON object if it's not in the selectedItems list
  jsonItems = selectedItems.filter((item) => item.item_quantity > 0);

  // Log the selected item
  // console.log('----------------');
  if (selectedItemIndex !== -1) {
    //   console.log('selectedItem::' + selectedItems[selectedItemIndex].currentQuantity + "-" + selectedItems[selectedItemIndex].sub_cat_name);
  }
  //console.log('----------------');
  //console.log("selectedItems: " + JSON.stringify(selectedItems));
  //console.log('----------------');
  //console.log('jsonItems: ' + JSON.stringify(jsonItems));
});

// Function to show a toast message
function showToast(message, bodyContent) {
  // Get the toast element and its content
  var toastElement = document.getElementById("liveToast");
  var toastBody = toastElement.querySelector(".toast-body");

  // Update the toast content with the provided message and body content
  toastBody.textContent = bodyContent;

  // Show the toast
  var toast = new bootstrap.Toast(toastElement);
  toast.show();
}

var dataCat = {};

function loadSubCategories(categorySelect) {
  var selectedCategory = $(categorySelect).val();
  var cat_id = $(categorySelect).find(":selected").data("catids");
  var cat_img = $(categorySelect).find(":selected").data("cat_img");
  var cat_name = $(categorySelect).find(":selected").data("cat_name");
  console.log("CatID::" + cat_id);
  console.log("CatIMG::" + cat_img);
  console.log("CatName::" + cat_name);

  selectedCategoryId = cat_id;
  selectedCategoryImage = cat_img;
  selectedCategoryName = cat_name;

  selectedItems = [];
  var sectionSelect = $("#input-section");
  var section_column = $("#section_col");
  var price_column = $("#price_col");

  //To Hide and

  var only_dry_clean_column = $("#other-then-dry-clean");
  var price_column = $("#price_col");
  //var subCategorySelect = $('#input-subcategory');
  var subCategoryTable = $("#subCategoryTable tbody");
  var priceSelect = $("#input-price");

  //Extra Headers
  // var costTh = $("<th class='text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 ps-2 w-25'>Cost</th>");
  //var emptyTh = $("<th class='text-secondary opacity-7'></th>");

  console.log("selectedCategory::" + selectedCategory);
  if (selectedCategory == "DRY CLEAN") {
    //Load Sections Here
    //$("#subCategoryTable").find("thead tr").remove(costTh);
    //$("#subCategoryTable").find("thead tr").append(costTh);
    //$("#subCategoryTable").find("thead tr").append(emptyTh);

    subCategoryTable.empty();

    section_column.show();
    price_column.hide();
    only_dry_clean_column.hide(); //to not show KGS Add Quantity
    // subCategorySelect.empty();
    //subCategorySelect.append('<option disabled selected>Choose Sub Category</option>');
    $.get(`/admin_dashboard/load_sub_categories/${cat_id}`, function (data) {
      sectionSelect.empty();
      sectionSelect.append("<option disabled selected>Choose Section</option>");
      console.log("sectionSelect::" + sectionSelect);
      $.each(data.section_data, function (index, subSection) {
        sectionSelect.append(
          $("<option>", {
            value: subSection.section_name,
            text: subSection.section_name,
          })
        );
      });
    });
  } else {
    // $("#subCategoryTable").find("thead tr").append(emptyTh);
    //$("#subCategoryTable").find("thead tr").remove(costTh);
    section_column.hide();
    only_dry_clean_column.show();
    price_column.show();
    $.get(
      `/admin_dashboard/load_section_type_sub_categories/All`,
      function (data) {
        /*subCategorySelect.empty();
            subCategorySelect.append('<option disabled selected>Choose Sub Category</option>');
    
            $.each(data.sub_categories, function(index, subCategory) {
                subCategorySelect.append($('<option>', {
                    value: subCategory.subcatid,
                    text: subCategory.sub_cat_name
                }));
            });*/

        subCategoryTable.empty(); // Clear any existing rows
        console.log("subCategoryTable:" + subCategoryTable);
        dataCat = data.sub_categories;
        $.each(data.sub_categories, function (index, subCategory) {
          var newRow = $("<tr>");
          newRow.append(
            "<td> <div id='sub_catid' style='display:none;'>" +
              subCategory.subcatid +
              "</div>" +
              "<div id='sub_cat_img' style='display:none;'>" +
              subCategory.sub_cat_img +
              "</div>" +
              "<div id='cost' style='display:none;'>" +
              subCategory.cost +
              "</div>" +
              "<div id='type' style='display:none;'>" +
              subCategory.type +
              "</div>" +
              "<div id='cat_id' style='display:none;'>" +
              cat_id +
              "</div>" +
              "<div id='cat_img' style='display:none;'>" +
              cat_img +
              "</div>" +
              "<div id='cat_name' style='display:none;'>" +
              cat_name +
              "</div>" +
              "<div id='selectedCategory' style='display:none;'>" +
              selectedCategory +
              "</div> <div id='subCategory' style='display:none;'>" +
              subCategory +
              "</div>" +
              "<div class='d-flex px-2 py-1'> <div class='d-flex px-2 py-1'><img src=" +
              subCategory.sub_cat_img +
              " class='avatar avatar-sm me-3' alt='user1'> </div> <div class='d-flex flex-column justify-content-center'> <h6 class='mb-0 text-sm' id='sub_cat_name'>" +
              subCategory.sub_cat_name +
              "</h6></div></div> </div> </td>"
          );
          //newRow.append("<td> <p class=\"text-xs font-weight-bold mb-0\">" + subCategory.sub_cat_name + "</p></td>");
          /* newRow.append("<td><input type='number' value='0' min='0'></td>"); 
newRow.append("<td>  <div class=\"d-flex px-2 py-1\"> <p class=\"mb-0 text-xxs text-center\"> " + subCategory.cost +'/ '+subCategory.type + " </p></div></td>");
newRow.append("<td>  <p class=\"text-xxs font-weight-bold mb-0\">" + ${subCategory.type} + "</p></td>");
newRow.append("<td><button class='btn btn-danger btn-sm ms-1 increment'>+</button><input class='m-2' type='number' value='0' min='0'><button class='btn btn-success btn-sm ms-1 decrement'>-</button></td>");*/
          newRow.append(
            '<td style="vertical-align: middle; ">  <div class="btn-group btn-group-sm mt-2" style="width: 5px; display: flex; align-items: center;" role="group" aria-label="Basic mixed styles example"> <button type="button" class="btn btn-danger btn-sm decrement" style="width: 10px;" >-</button><button type="button" class="btn btn-sm quantity" style="width: 10px;" >0</button><button type="button" class="btn btn-success btn-sm increment" style="width: 10px;" >+</button> </td>'
          );

          subCategoryTable.append(newRow);
        });
      }
    );
    console.log("While Loading CatID::" + cat_id);
    $.get(
      `/admin_dashboard/load_other_category_wise_details/${cat_id}`,
      function (data) {
        console.log("priceCategory::" + data.other_category_data);
        priceCategory = data.other_category_data;

        priceSelect.empty();
        priceSelect.append(
          "<option disabled selected>Choose Service Type</option>"
        );
        // Access and use the properties of the priceCategory object here
        // Regular Price

        priceSelect.append(
          $("<option>", {
            value: `Regular Price ${priceCategory.regular_price} [${priceCategory.regular_price_type}] `,
            text: `Regular Price ${priceCategory.regular_price} [${priceCategory.regular_price_type}] `,
          })
        );

        // Express Price
        /* priceSelect.append($('<optgroup>', {
    label: 'Express Price',
}));
*/
        priceSelect.append(
          $("<option>", {
            value: `Express Price ${priceCategory.express_price} [${priceCategory.express_price_type}] `,
            text: `Express Price ${priceCategory.express_price} [${priceCategory.express_price_type}] `,
          })
        );

        // Offer Price
        priceSelect.append(
          $("<option>", {
            value: `Offer Price ${priceCategory.offer_price} [${priceCategory.offer_price_type}] `,
            text: `Offer Price ${priceCategory.offer_price} [${priceCategory.offer_price_type}] `,
          })
        );
      }
    );
  }
}

function loadSubCategoriesBySection(sectionTypeSelect) {
  var section_type = $(sectionTypeSelect).val();
  var categorySelect = $("#input-category").val();
  var cat_id = $(categorySelect).find(":selected").data("catids");
  var section_id = $(sectionTypeSelect).find(":selected").data("section_id");
  var cat_img = $(categorySelect).find(":selected").data("cat_img");
  var cat_name = $(categorySelect).find(":selected").data("cat_name");
  selectedItems = [];
  console.log("CatID::" + cat_id);
  console.log("CatIMG::" + cat_img);
  console.log("CatName::" + cat_name);

  console.log("section_id::" + section_id);
  console.log("section_type::" + section_type);

  var sectionSelect = $("#input-section");
  var subCategoryTable = $("#subCategoryTable tbody");
  //var subCategorySelect = $('#input-subcategory');

  $.get(
    `/admin_dashboard/load_section_type_sub_categories/${section_type}`,
    function (data) {
      subCategoryTable.empty(); // Clear any existing rows

      $.each(data.sub_categories, function (index, subCategory) {
        var newRow = $("<tr>");
        newRow.append(
          "<td> <div id='sub_catid' style='display:none;'>" +
            subCategory.subcatid +
            "</div>" +
            "<div id='sub_cat_img' style='display:none;'>" +
            subCategory.sub_cat_img +
            "</div>" +
            "<div id='cost' style='display:none;'>" +
            subCategory.cost +
            "</div>" +
            "<div id='type' style='display:none;'>" +
            subCategory.type +
            "</div>" +
            "<div id='cat_id' style='display:none;'>" +
            cat_id +
            "</div>" +
            "<div id='cat_img' style='display:none;'>" +
            cat_img +
            "</div>" +
            "<div id='cat_name' style='display:none;'>" +
            cat_name +
            "</div>" +
            "<div id='section_type' style='display:none;'>" +
            section_type +
            "</div>" +
            "<div class='d-flex px-2 py-1'> <div class='d-flex px-2 py-1'><img src=" +
            subCategory.sub_cat_img +
            " class='avatar avatar-sm me-3' alt='user1'> </div> <div class='d-flex flex-column justify-content-center'> <h6 class='mb-0 text-sm' id='sub_cat_name'>" +
            subCategory.sub_cat_name +
            "</h6> <p class='text-xs text-secondary mb-0'>" +
            subCategory.cost +
            "/ " +
            subCategory.type +
            "</p> </div></div> </div> </td>"
        );

        //newRow.append("<td>  <div class=\"d-flex px-2 py-1\"> <p class=\"mb-0 text-xxs text-center\"> " + subCategory.cost +'/ '+subCategory.type + " </p></div></td>");
        /* newRow.append("<td><input type='number' value='0' min='0'></td>"); 
newRow.append("<td>  <p class=\"text-xxs font-weight-bold mb-0\">" + ${subCategory.type} + "</p></td>");
newRow.append("<td><button class='btn btn-danger btn-sm ms-1 increment'>+</button><input class='m-2' type='number' value='0' min='0'><button class='btn btn-success btn-sm ms-1 decrement'>-</button></td>");*/
        newRow.append(
          '<td style="vertical-align: middle; ">  <div class="btn-group btn-group-sm mt-2" style="width: 5px; display: flex; align-items: center;" role="group" aria-label="Basic mixed styles example"> <button type="button" class="btn btn-danger btn-sm decrement" style="width: 10px;" >-</button><button type="button" class="btn btn-sm quantity" style="width: 10px;" >0</button><button type="button" class="btn btn-success btn-sm increment" style="width: 10px;" >+</button> </td>'
        );

        subCategoryTable.append(newRow);
      });
      /*subCategorySelect.empty();
            subCategorySelect.append('<option disabled selected>Choose Sub Category</option>');
    
            $.each(data.sub_categories, function(index, subCategory) {
                subCategorySelect.append($('<option>', {
                    value: subCategory.subcatid,
                    text: subCategory.sub_cat_name
                }));
            });*/
    }
  );
}

$(document).ready(function () {
  const inputField = $("#customer-name");
  const suggestionContainer = $("#suggestion-container");
  const suggestionList = $("#suggestion-list");
  const selectedCustomerIdInput = $("#selected-customer-id");
  const selectedMobileNoInput = $("#selected-mobile-no");
  const selectedCustomerNameInput = $("#selected-customer-name");

  inputField.on("input", function () {
    const inputText = inputField.val();
    suggestionContainer.show();
    if (inputText.length > 0) {
      $.get(
        `/admin_dashboard/search_customer_to_assign_order/${inputText}/`,
        function (data) {
          const suggestions = data.suggestions;
          suggestionList.empty();

          if (suggestions.length > 0) {
            suggestions.forEach(function (suggestion) {
              const suggestionItem = $('<li class="nav-item">').text(
                suggestion.customer_name
              );
              suggestionItem.on("click", function () {
                // When a suggestion is clicked, set the value in the input field
                inputField.val(suggestion.customer_name);

                // Set the selected customer details in hidden inputs
                selectedCustomerIdInput.val(suggestion.consmrid);
                selectedMobileNoInput.val(suggestion.mobile_no);
                selectedCustomerNameInput.val(suggestion.customer_name);

                // Hide the suggestions list (ul)
                suggestionContainer.hide();

                // Hide the popover
                inputField.popover("hide");
              });
              suggestionList.append(suggestionItem);
            });
          }
        }
      );
    } else {
      suggestionList.empty();
    }
  });

  inputField.focus(function () {
    // Display the suggestions container when the input field is focused
    suggestionContainer.show();
  });

  inputField.focusout(function () {
    // Hide the popover when the input field loses focus
    inputField.popover("hide");
  });
});

$(document).ready(function () {
  const inputField = $("#customer-name");
  const suggestionContainer = $("#suggestion-container");
  const selectedCustomerInput = $("#selected-customer");

  inputField.on("input", function () {
    const inputText = inputField.val();

    if (inputText.length > 0) {
      $.get(
        `/admin_dashboard/search_customer_to_assign_order/${inputText}/`,
        function (data) {
          const suggestions = data.suggestions;
          suggestionContainer.empty();

          if (suggestions.length > 0) {
            const suggestionList = $("<ul>");
            suggestions.forEach(function (suggestion) {
              const suggestionItem = $("<li>").text(suggestion.customer_name);
              suggestionItem.on("click", function () {
                // When a suggestion is clicked, set the value in the input field
                selectedCustomerInput.val(suggestion.customer_name);
              });
              suggestionList.append(suggestionItem);
            });
            suggestionContainer.append(suggestionList);
          }
        }
      );
    } else {
      suggestionContainer.empty();
    }
  });

  inputField.focusout(function () {
    // Clear suggestions when the input field loses focus.
    suggestionContainer.empty();
  });
});
