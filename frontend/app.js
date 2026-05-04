// Biến lưu trữ Token JWT sau khi đăng nhập
let accessToken = null;

// 1. GỌI PRODUCT SERVICE (Lấy danh sách sản phẩm)
async function loadProducts() {
    try {
        // Nginx sẽ tự bẻ lái cái này sang Product Service (Cổng 8013)
        const response = await fetch('/api/products/'); 
        const products = await response.json();
        
        const productList = document.getElementById('productList');
        productList.innerHTML = ''; // Xóa nội dung cũ

        products.forEach(p => {
            productList.innerHTML += `
                <div class="col-md-3 mb-4">
                    <div class="card h-100 shadow-sm">
                        <div class="card-body">
                            <h5 class="card-title text-truncate">${p.name}</h5>
                            <p class="card-text text-danger fw-bold">${p.price} VNĐ</p>
                            <p class="card-text small text-muted">Kho: ${p.stock}</p>
                            <button class="btn btn-primary w-100" onclick="addToCart(${p.id})">Thêm vào giỏ</button>
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error("Lỗi tải sản phẩm:", error);
    }
}

// 2. GỌI USER SERVICE (Giả lập đăng nhập nhanh)
async function login() {
    // Để cho nhanh, thay vì tạo form, mình hardcode tài khoản bạn đã tạo trong DB
    const username = prompt("Nhập username:", "admin");
    const password = prompt("Nhập mật khẩu:", "1230");

    if(!username || !password) return;

    try {
        // Nginx bẻ lái sang User Service
        const res = await fetch('/api/users/api/token/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        const data = await res.json();
        if (data.access) {
            accessToken = data.access;
            document.getElementById('userInfo').innerText = `Xin chào, ${username}!`;
            document.getElementById('loginBtn').classList.add('d-none');
            alert("Đăng nhập thành công! Đã lấy được JWT Token.");
        } else {
            alert("Sai tài khoản hoặc mật khẩu!");
        }
    } catch (error) {
        alert("Lỗi kết nối đến User Service.");
    }
}

// 3. GỌI CART SERVICE (Thêm hàng)
async function addToCart(productId) {
    if (!accessToken) {
        alert("Vui lòng đăng nhập trước khi mua hàng!");
        return;
    }

    try {
        // Nginx bẻ lái sang Cart Service
        const res = await fetch('/api/cart/add/', {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${accessToken}`
            },
            body: JSON.stringify({ product_id: productId, quantity: 1 })
        });

        if (res.ok) {
            let count = parseInt(document.getElementById('cartCount').innerText);
            document.getElementById('cartCount').innerText = count + 1;
        } else {
            alert("Lỗi khi thêm vào giỏ hàng!");
        }
    } catch (error) {
        console.error(error);
    }
}

// 4. GỌI ORDER SERVICE (Chốt đơn)
async function checkout() {
    if (!accessToken) {
        alert("Bạn chưa đăng nhập!"); return;
    }
    
    if (confirm("Bạn có chắc chắn muốn chốt toàn bộ giỏ hàng không?")) {
        try {
            // Nginx bẻ lái sang Order Service, Order sẽ tự gọi Cart và Product
            const res = await fetch('/api/orders/checkout/', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${accessToken}` }
            });
            const data = await res.json();
            
            if (res.status === 201) {
                alert(data.message + "\nTổng tiền: " + data.order.total_amount + " VNĐ");
                document.getElementById('cartCount').innerText = "0"; // Reset giỏ
            } else {
                alert("Lỗi: " + data.error);
            }
        } catch (error) {
            console.error(error);
        }
    }
}

// Khi trang vừa load lên thì tự động gọi lấy sản phẩm
window.onload = loadProducts;