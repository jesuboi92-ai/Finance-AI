import base64
import io
import pandas as pd
import pypdf
from PIL import Image
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Talous-AI & Vaurastumisassistentti", page_icon="📈", layout="centered"
)

st.title("📈 Talous-AI & Vaurastumisassistentti (Pro)")
st.write(
    "Kattava talousvalmentaja, sijoituspuskurin laskija, älykäs budjetoija "
    "sekä tarkalla gpt-4o -kuvaskannerilla varustettu työkalu."
)

# Sivupalkki asetuksille
st.sidebar.header("⚙️ Asetukset & Versio")
app_mode = st.sidebar.selectbox(
    "Valitse tila", ["Ilmaisversio (Free)", "Pro-versio (Testaa)"]
)
api_key = st.sidebar.text_input("Syötä OpenAI API-avain", type="password")

# Pääsovelluksen välilehdet
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📝 Manuaaliset menot", 
        "🎯 Sijoituspuskuri", 
        "💡 Smart Budget", 
        "🛒 Perusruokabudjetti",
        "🏷️ Omat Hinnat & Kuittiskanneri",
        "🍳 Ruokalista & Tuotevertailu"
    ]
)

# Alustetaan muuttujat session stateen
if "custom_products" not in st.session_state:
    st.session_state.custom_products = pd.DataFrame(
        [
            {"Poista": False, "Tuote / Pakkaus": "Kanafilee (400g)", "Kauppa": "Prisma", "Hinta (€)": 4.50},
            {"Poista": False, "Tuote / Pakkaus": "Maito (1l)", "Kauppa": "S-Market", "Hinta (€)": 1.19},
            {"Poista": False, "Tuote / Pakkaus": "Raejuusto (400g)", "Kauppa": "Prisma", "Hinta (€)": 2.15},
            {"Poista": False, "Tuote / Pakkaus": "Banaanit (niput)", "Kauppa": "Lidl", "Hinta (€)": 2.50},
            {"Poista": False, "Tuote / Pakkaus": "Riisi (1kg)", "Kauppa": "K-Citymarket", "Hinta (€)": 1.60},
        ]
    )

if "uploaded_image_records" not in st.session_state:
    st.session_state.uploaded_image_records = []


def compress_image(image_bytes, max_size=1600):
    """Optimoitu tarkkuus: sallitaan suurempi resoluutio (1600px), jotta teksti on varmasti luettavissa."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.thumbnail((max_size, max_size))
        buffered = io.BytesIO()
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.save(buffered, format="JPEG", quality=90)
        return buffered.getvalue()
    except Exception:
        return image_bytes


def encode_image(image_bytes):
    compressed_bytes = compress_image(image_bytes)
    return base64.b64encode(compressed_bytes).decode("utf-8")


with tab1:
    st.subheader("1. Tulot ja manuaaliset elämisen kulut")
    col1, col2 = st.columns(2)
    with col1:
        monthly_income = st.number_input("Netto-kuukausitulot (€)", min_value=0.0, value=2500.0, step=50.0)
        vuokra = st.number_input("Vuokra / Asuntolaina (€)", min_value=0.0, value=800.0, step=50.0)
        sahko = st.number_input("Sähkö (€)", min_value=0.0, value=40.0, step=10.0)
        vesi = st.number_input("Vesi (€)", min_value=0.0, value=20.0, step=5.0)
    with col2:
        ruokakulut = st.number_input("Arvioidut ruokakulut (kauppa) (€)", min_value=0.0, value=350.0, step=25.0)
        suoratoisto = st.number_input("Suoratoistopalvelut (€)", min_value=0.0, value=45.0, step=5.0)
        muut_menot = st.number_input("Muut pakolliset kulut (€)", min_value=0.0, value=150.0, step=25.0)

    total_expenses = vuokra + sahko + vesi + ruokakulut + suoratoisto + muut_menot
    net_left = monthly_income - total_expenses
    st.info(f"📊 Yhteenveto: Tulot {monthly_income} € | Menot **{total_expenses} €** | Jäljelle jää: **{net_left} €**")

with tab2:
    st.subheader("2. Sijoittamiskeskeinen optimointi & Puskurivara")
    current_balance = st.number_input("Tilillä oleva nykyinen käyttöraha yhteensä (€)", value=3500.0)
    buffer_need = st.number_input("Turvapuskurin tavoite (€)", value=2000.0)

    if st.button("Laske sijoitettava ylijäämä"):
        excess_cash = current_balance - buffer_need
        if excess_cash > 0:
            st.success(
                f"💡 **Sijoituspotentiaali:** Tililläsi on noin **{excess_cash:.0f} euroa** "
                "ylimääräistä puskurin ylittävää rahaa."
            )
        else:
            st.info("Keskity ensin saavuttamaan turvapuskuritavoite.")

with tab3:
    st.subheader("3. Smart Budget & Viikkoseuranta")
    weekly_food_target = st.number_input("Asetettu viikoittainen ruokabudjetti (€)", value=80.0)
    actual_food_spent = st.number_input("Tällä viikolla ruokaan käytetty (€)", value=65.0)
    
    if st.button("Hae palaute viikon kulutuksesta"):
        if not api_key:
            st.warning("Syötä sivupalkkiin OpenAI API-avain.")
        else:
            client = OpenAI(api_key=api_key)
            prompt = f"Arvioi viikoittaista ruokabudjettia (tavoite: {weekly_food_target} €, toteutunut: {actual_food_spent} €) huumorilla ja anna vinkkejä."
            resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            st.markdown(resp.choices[0].message.content)

with tab4:
    st.subheader("4. Perusruokabudjetoija & Kauppavinkit")
    family_size = st.selectbox("Talouden koko", ["1 henkilö", "2 henkilöä", "Perhe"])
    if st.button("Luo perusopas"):
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": f"Anna budjettivinkit ruokakauppaan taloudelle: {family_size}"}])
        st.markdown(resp.choices[0].message.content)

with tab5:
    st.subheader("🏷️ Omat tuotehinnat, Kaupat & Älykäs Kuvaskanneri")
    st.write("Lataa kauppojen näyttökuvat tai kuitit. Aiemmin lisätyt tai järjestelmään kertaalleen tallennetut kuvat merkitään selkeän **punaiseksi**.")

    col_c1, col_c2 = st.columns([1, 1])

    with col_c1:
        st.markdown("### 📸 Monikuva- / Näyttökuvaskanneri")
        
        default_store_choice = st.selectbox(
            "Valitse oletuskauppa (jos kuvasta ei selviä):",
            ["Päättele kuvasta", "Prisma", "S-Market", "Lidl", "K-Citymarket", "K-Market", "Alepa", "Sale"]
        )

        uploaded_files = st.file_uploader(
            "Lataa kauppojen näyttökuvat tai kuitit", 
            type=["png", "jpg", "jpeg"], 
            accept_multiple_files=True
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                
                # Tarkistetaan, löytyykö täsmälleen sama tiedosto (nimi + sisältö) jo listalta
                exists_already = any(
                    item["name"] == uploaded_file.name and item["data"] == file_bytes 
                    for item in st.session_state.uploaded_image_records
                )
                
                if not exists_already:
                    st.session_state.uploaded_image_records.append({
                        "name": uploaded_file.name,
                        "data": file_bytes,
                        "type": "image/jpeg",
                        "already_added": False
                    })

        if st.session_state.uploaded_image_records:
            st.markdown("#### Ladatut kuvat & hallinta (Rastita poistaaksesi)")
            
            updated_records = []
            for i, record in enumerate(st.session_state.uploaded_image_records):
                # Jos kuva on jo kertaalleen analysoitu (already_added == True) tai sama nimi esiintyy useasti, näytetään punaisena
                name_count = sum(1 for r in st.session_state.uploaded_image_records if r["name"] == record["name"])
                is_red = name_count > 1 or record.get("already_added", False)

                if is_red:
                    st.markdown(
                        f"""<div style="border: 3px solid #ff4d4d; background-color: #ffe6e6; padding: 12px; border-radius: 8px; margin-bottom: 8px;">
                        <span style="color: #cc0000; font-weight: bold; font-size: 15px;">🛑 Jo lisätty / Käsitelty aiemmin: {record['name']}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""<div style="border: 2px solid #4CAF50; background-color: #e8f5e9; padding: 10px; border-radius: 8px; margin-bottom: 8px;">
                        <span style="color: #2e7d32; font-weight: bold;">✨ Uusi kuva: {record['name']}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
                
                cols = st.columns([3, 1])
                with cols[0]:
                    st.image(record["data"], caption=record["name"], width=160)
                with cols[1]:
                    remove_flag = st.checkbox("Poista", key=f"del_img_{i}")
                
                if not remove_flag:
                    updated_records.append(record)
                else:
                    st.warning(f"Poistettu kuva: {record['name']}")
            
            st.session_state.uploaded_image_records = updated_records

        if st.session_state.uploaded_image_records and st.button("Pura tuotteet, kaupat ja tarkat hinnat kuvista (Tarkka analyysi)"):
            if not api_key:
                st.warning("Syötä sivupalkkiin OpenAI API-avain.")
            else:
                with st.spinner("Tekoäly (gpt-4o) tutkii kuvia perusteellisesti ja poimii jokaisen tuotteen, pakkauskoon ja hinnan... (tämä voi kestää hetken)"):
                    client = OpenAI(api_key=api_key)
                    
                    store_inst = f"Käytä oletuskauppana '{default_store_choice}' jos kauppaa ei selvästi mainita. " if default_store_choice != "Päättele kuvasta" else "Tunnista aina kaupan nimi (esim. Prisma, S-Market, Lidl, K-Citymarket, K-Market) suoraan kuvasta. "
                    
                    messages_content = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        f"Olet äärimmäisen tarkka kauppa-, tuote- ja hintatietojen asiantuntija. {store_inst} "
                                        "Käy läpi jokainen alla oleva kuva yksityiskohtaisesti, skannaa kaikki tuoterivit, tuotenimet, pakkauskoot (esim. 400g, 1l) sekä hinnat euroina (€). "
                                        "Älä ohita yhtään tuotetta. Jos hinnassa tai tuotteessa on epäselvyyttä, tulkitse se mahdollisimman tarkasti kuvan perusteella.\n\n"
                                        "Palauta tulos selkeänä taulukkona tai listana muodossa:\n"
                                        "Tuote / Pakkaus | Kauppa | Hinta (€)\n\n"
                                        "Listaa lopuksi yhteenveto havaituista kuvista ja tuotteista."
                                    )
                                }
                            ]
                        }
                    ]

                    for record in st.session_state.uploaded_image_records:
                        base64_img = encode_image(record["data"])
                        messages_content[0]["content"].append({
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            }
                        })
                        # Merkitään, että tämä kuva on nyt käsitelty, jotta se näkyy jatkossa varmasti punaisena
                        record["already_added"] = True

                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages_content,
                        max_tokens=2000,
                        temperature=0.1
                    )

                    st.success("Tarkka kuvien analyysi valmis!")
                    st.markdown("### 🔍 Löydetyt tuotteet, kaupat ja hinnat:")
                    extracted_text = response.choices[0].message.content
                    st.markdown(extracted_text)

    with col_c2:
        st.markdown("### 📋 Omat tallennetut hinnat & kaupat")
        edited_df = st.data_editor(st.session_state.custom_products, num_rows="dynamic", key="product_editor")
        
        if "Poista" in edited_df.columns:
            st.session_state.custom_products = edited_df[edited_df["Poista"] == False].reset_index(drop=True)
        else:
            st.session_state.custom_products = edited_df

with tab6:
    st.subheader("🍳 Tarkasti kaloroitu ruokalista & Kauppojen vertailu")
    st.write("Suunnittele ruokalista ja vertaile hintoja kaupoittain omien tallennettujen hintojen pohjalta.")

    col_a, col_b = st.columns(2)
    with col_a:
        diet_choice = st.selectbox("Valitse ruokavalio", ["Sekasyöjä", "Kasvissyöjä", "Vegaani", "Gluteeniton", "Laktoositon"])
        daily_calories = st.number_input("Päivittäinen kaloritavoite (kcal)", min_value=1200, max_value=4000, value=2000, step=50)
        days_count = st.slider("Suunniteltava ajanjakso (päivää)", min_value=1, max_value=7, value=7)
    with col_b:
        goal_choice = st.selectbox("Optio / Tavoite", ["📉 Laihdutus / Painonhallinta (Kalorivaje)", "Halvin mahdollinen", "Proteiinipitoinen / Fitness"])
        meals_per_day = st.slider("Aterioiden määrä per päivä", min_value=1, max_value=6, value=3)

    allergies_input = st.text_input("Erityisallergiat tai vältettävät aineet", value="")
    stores_to_compare = st.multiselect("Valitse huomioitavat kaupat", ["Lidl", "S-Market", "Prisma", "K-Market", "K-Citymarket"], default=["Lidl", "Prisma", "S-Market"])

    if st.button("Generoi viikon ruokalista ja kauppakohtainen vertailu"):
        if not api_key:
            st.warning("Syötä sivupalkkiin OpenAI API-avain.")
        else:
            client = OpenAI(api_key=api_key)
            prompt = f"Luo {days_count} päivän ruokalista tavoitteella {goal_choice} ja kaloreilla {daily_calories}."
            resp = client.chat.completions.create(model="gpt-4o", messages=[{"role": "user", "content": prompt}])
            st.markdown(resp.choices[0].message.content)
