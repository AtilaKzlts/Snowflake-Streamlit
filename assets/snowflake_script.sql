def calculate_elasticity_regression(price_data, quantity_data, competitor_price_data, promotion_data):
    """Fiyat esnekliğini hesaplayan fonksiyon"""
    
    # Log dönüşümü (esneklik hesaplama için)
    log_price = np.log(price_data)
    log_quantity = np.log(quantity_data)
    log_competitor_price = np.log(competitor_price_data)
    
    # Promosyonu binary değişkene çevir
    promotion = promotion_data.map({'No': 0, 'Yes': 1})
    
    # Geçersiz verileri filtrele (log(0) hatasını önlemek için)
    mask = np.isfinite(log_quantity) & np.isfinite(log_price) & np.isfinite(log_competitor_price)
    log_price = log_price[mask]
    log_quantity = log_quantity[mask]
    log_competitor_price = log_competitor_price[mask]
    promotion = promotion[mask]
    
    # Bağımsız değişkenleri oluştur
    X = np.column_stack([log_price, log_competitor_price, promotion])
    X = sm.add_constant(X)  # Sabit terimi ekle

    # Çoklu doğrusal regresyon modeli oluştur
    model = sm.OLS(log_quantity, X).fit()
    
    # Sonuçları döndür
    return {
        'elasticity': model.params.iloc[1],  # Fiyat esnekliği
        'competitor_elasticity': model.params.iloc[2],  # Rakip fiyat esnekliği
        'promotion_effect': model.params.iloc[3],  # Promosyon etkisi
        'r_squared': model.rsquared,
        'p_value': model.pvalues.iloc[1],  # Fiyat katsayısı p-değeri
        'std_error': model.bse.iloc[1]  # Standart hata
    }

# Esneklik hesaplama
results = calculate_elasticity_regression(
    product_data['price'],
    product_data['sales_quantity'],
    product_data['competitor_price'],
    product_data['promotion']
)

# Sonuçları yazdırma
print(f"Fiyat Esnekliği: {results['elasticity']:.2f}")
print(f"Rakip Fiyat Esnekliği: {results['competitor_elasticity']:.2f}")
print(f"Promosyon Etkisi: {results['promotion_effect']:.2f}")
print(f"R-kare: {results['r_squared']:.2f}")
print(f"P-değeri (Fiyat): {results['p_value']:.4f}")
print(f"Fiyatın Standart Hatası: {results['std_error']:.4f}")