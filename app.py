import base64
import io
import pandas as pd
import pypdf
from PIL import Image
import streamlit as st
from openai import OpenAI

st.set_page_config(
    page_title="Talous-AI & Vaurastumisassistentti (Ultimate)", page_icon="📈", layout="centered"
)

st.title("📈 Talous-AI & Vaurastumisassistentti (Ultimate Pro)")
st.write(
    "Kaikki toiminnot samassa: Palkkalaskelman PDF-luku, tulot ja menot, sijoituslaskurit & kriittinen AI, "
    "Smart Budget, älykäs kuvaskanneri, perusruokabudjetti sekä kaloroitu ruokalistasuunnittelija."
)

# Sivupalkki asetuksille
st.sidebar.header("⚙️ Asetukset & Versio")
app_mode = st.sidebar.selectbox(
    "Valitse tila", ["Ilmaisversio (Free)", "Pro-versio (Testaa)"]
)
api_key = st.sidebar.text_input("Syötä OpenAI API-avain", type="password")

# Pääsovelluksen kaikki 6 välilehteä
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📝 Tulot, PDF & Menot", 
        "🎯 Sijoituspuskuri & AI-analyysi", 
        "💡 Smart Budget", 
        "🏷️ Hinnat & Kuittiskanneri",
        "🛒 Perusruokabudjetti",
        "🍳 Ruokalista & Vertailu"
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


# --- TAB 1: TULOT, PDF & MENOT ---
with tab1:
    st.subheader("1. Tulot (myös PDF-palkkalaskelman luku) & Manuaaliset menot")
    
    st.markdown("### 📄 Tuo tulotiedot suoraan PDF-palkkalaskelmasta")
    uploaded_pdf = st.file_uploader("Lataa palkkalaskelma (PDF)", type=["pdf"], key="pdf_uploader_main")
    
    if uploaded_pdf is not None:
        try:
            reader = pypdf.PdfReader(uploaded_pdf)
            pdf_text = ""
            for page in reader.pages:
                pdf_text += page.extract_text() or ""
            
            if api_key and pdf_text.strip():
                with st.spinner("Tekoäly lukee palkkatietoja PDF:stä..."):
                    client = OpenAI(api_key=api_key)
                    prompt = (
                        "Etsi seuraavasta palkkalaskelman tekstistä NETTO-palkka (käteen jäävä summa) "
                        "sekä BRUTTO-palkka. Palauta tulos muodossa: Netto: [numero], Brutto: [numero].\n\n"
                        f"Teksti:\n{pdf_text[:3000]}"
                    )
                    resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                    st.info(f"AI:n löytämät tiedot tekstistä: {resp.choices[0].message.content}")
            else:
                st.write("PDF luettu (syötä API-avain sivupalkkiin, jos haluat tekoälyn jäsentävän summan automaattisesti).")
        except Exception as e:
            st.error(f"Virhe PDF-tiedoston lukemisessa: {e}")

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


# --- TAB 2: SIJOITUSPUSKURI & AI-ANALYYSI ---
with tab2:
    st.subheader("2. Sijoittamiskeskeinen optimointi, Markkinatuoton laskenta & Kriittinen AI-analyysi")
    current_balance = st.number_input("Tilillä oleva nykyinen käyttöraha yhteensä (€)", value=3500.0, key="curr_bal")
    buffer_need = st.number_input("Turvapuskurin tavoite (€)", value=2000.0, key="buff_need")

    if st.button("Laske sijoitettava ylijäämä"):
        excess_cash = current_balance - buffer_need
        if excess_cash > 0:
            st.success(
                f"💡 **Sijoituspotentiaali:** Tililläsi on noin **{excess_cash:.0f} euroa** "
                "ylimääräistä puskurin ylittävää rahaa."
            )
        else:
            st.info("Keskity ensin saavuttamaan turvapuskuritavoite.")

    st.markdown("---")
    st.markdown("### 📈 Markkinatuotto- ja Korkoa korolle -laskuri")
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        alkup_sijoitus = st.number_input("Alkusijoitus (€)", value=1000.0, step=100.0)
        kk_sijoitus = st.number_input("Kuukausisäästö / -sijoitus (€)", value=150.0, step=25.0)
    with col_inv2:
        sijoitus_aika_vuotta = st.slider("Sijoitusaika (vuotta)", 1, 40, 10)
        arvioitu_tuotto_prosentti = st.slider("Arvioitu vuosituotto (%)", 0.0, 20.0, 7.0, 0.5)

    kokonaissumma = alkup_sijoitus
    kuukausi_tuotto = arvioitu_tuotto_prosentti / 100 / 12
    kuukausia = sijoitus_aika_vuotta * 12

    sijoitettu_paoma_yhteensa = alkup_sijoitus
    for _ in range(kuukausia):
        kokonaissumma = (kokonaissumma + kk_sijoitus) * (1 + kuukausi_tuotto)
        sijoitettu_paoma_yhteensa += kk_sijoitus

    tuotto_yhteensa = kokonaissumma - sijoitettu_paoma_yhteensa

    st.info(
        f"📊 **Laskelman tulos ({sijoitus_aika_vuotta} vuoden jälkeen):**\n\n"
        f"- Sijoitettu pääoma yhteensä: **{sijoitettu_paoma_yhteensa:,.0f} €**\n"
        f"- Arvioitu voitto / tuotto: **{tuotto_yhteensa:,.0f} €**\n"
        f"- **Salkun arvo yhteensä:** **{kokonaissumma:,.0f} €**"
    )

    st.markdown("### 🤖 Kriittinen tekoälyanalyysi sijoitussuunnitelmasta")
    sijoitus_kohde_kuvaus = st.text_area(
        "Kerro lyhyesti mihin aiot sijoittaa (esim. globaalit indeksirahastot, kryptot tai osakkeet):",
        "Sijoitan kuukausittain maailma-indeksirahastoon ja toivon n. 7% keskimääräistä tuottoa."
    )

    if st.button("Pyydä kriittinen AI-analyysi sijoituksistasi"):
        if not api_key:
            st.warning("Syötä sivupalkkiin OpenAI API-avain.")
        else:
            client = OpenAI(api_key=api_key)
            prompt = (
                f"Olet äärimmäisen kriittinen ja kokenut sijoitusasiantuntija. "
                f"Analysoi seuraavaa sijoitussuunnitelmaa:\n"
                f"- Alkusijoitus: {alkup_sijoitus} €\n"
                f"- Kuukausisijoitus: {kk_sijoitus} €\n"
                f"- Sijoitusaika: {sijoitus_aika_vuotta} vuotta\n"
                f"- Oletettu vuosituotto: {arvioitu_tuotto_prosentti} %\n"
                f"- Strategia: {sijoitus_kohde_kuvaus}\n\n"
                "Ole rehellinen riskeistä (inflaatio, markkinoiden laskukaudet, verotus)."
            )
            with st.spinner("Tekoäly analysoi sijoituksiasi kriittisesti..."):
                resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                st.markdown(resp.choices[0].message.content)

    st.markdown("---")
    st.markdown("### 📊 Laajennettu sijoitusopas")
    sijoitus_vaihtoehto = st.selectbox(
        "Valitse omaisuuslaji, josta haluat lisätietoja:",
        ["Osakkeet & Indeksirahastot", "Korkosijoitukset", "Kiinteistöt & Asunnot", "Kryptovaluutat", "Vertaislainat"]
    )
    if sijoitus_vaihtoehto == "Osakkeet & Indeksirahastot":
        st.write("Hajautettu ja matalakuluinen tapa sijoittaa pitkällä aikavälillä (esim. ETF:ät).")
    elif sijoitus_vaihtoehto == "Korkosijoitukset":
        st.write("Turvallisempi vaihtoehto (säästötilit ja valtionlainat).")
    elif sijoitus_vaihtoehto == "Kiinteistöt & Asunnot":
        st.write("Tarjoaa vuokratuottoa, mutta vaatii pääomaa tai lainavipua.")
    elif sijoitus_vaihtoehto == "Kryptovaluutat":
        st.write("Korkean riskin ja volatiliteetin omaisuuslaji.")
    else:
        st.write("Lainanantoa alustojen kautta korkeammalla riskillä.")


# --- TAB 3: SMART BUDGET ---
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
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.markdown(resp.choices[0].message.content)


# --- TAB 4: HINNAT & KUITTISKANNERI ---
with tab4:
    st.subheader("🏷️ Omat tuotehinnat, Kaupat & Älykäs Kuvaskanneri")
    st.write("Lataa kauppojen näyttökuvat tai kuitit. Aiemmin lisätyt kuvat korostetaan punaisella, ja ne voi poistaa rastista.")

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
            accept_multiple_files=True,
            key="img_uploader_tab4"
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                existing_names = [item["name"] for item in st.session_state.uploaded_image_records]
                
                if uploaded_file.name not in existing_names:
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
                name_count = sum(1 for r in st.session_state.uploaded_image_records if r["name"] == record["name"])
                is_marked_red = name_count > 1 or record.get("already_added", False)

                if is_marked_red:
                    st.markdown(
                        f"""<div style="border: 2px solid red; background-color: #ffe6e6; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                        <span style="color: red; font-weight: bold;">🛑 Jo lisätty / Kaksoiskappale: {record['name']}</span>
                        </div>""", 
                        unsafe_allow_html=True
                    )
                
                cols = st.columns([3, 1])
                with cols[0]:
                    st.image(record["data"], caption=record["name"], width=150)
                with cols[1]:
                    remove_flag = st.checkbox("Poista", key=f"del_img_{i}")
                
                if not remove_flag:
                    updated_records.append(record)
                else:
                    st.warning(f"Poistettu kuva: {record['name']}")
            
            st.session_state.uploaded_image_records = updated_records

        if st.session_state.uploaded_image_records and st.button("Pura tuotteet, kaupat ja hinnat kuvista"):
            if not api_key:
                st.warning("Syötä sivupalkkiin OpenAI API-avain.")
            else:
                with st.spinner("Tekoäly analysoi kuvia ja poimii kaupat, tuotteet, pakkauskoot ja hinnat..."):
                    client = OpenAI(api_key=api_key)
                    store_inst = f"Käytä oletuskauppana '{default_store_choice}' jos kauppaa ei mainita. " if default_store_choice != "Päättele kuvasta" else "Tunnista aina kauppa suoraan kuvasta. "
                    
                    messages_content = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": (
                                        f"Olet tarkka hinta- ja kauppatietojen lukija. {store_inst} "
                                        "Käy läpi jokainen kuva ja poimi tuotteet, pakkauskoot ja hinnat euroina (€). "
                                        "Palauta tulos selkeänä taulukkona tai listana muodossa:\n"
                                        "Tuote / Pakkaus | Kauppa | Hinta (€)"
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
                        record["already_added"] = True

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_content,
                        max_tokens=1500
                    )

                    st.success("Kuvat analysoitu onnistuneesti!")
                    st.markdown("### 🔍 Löydetyt tuotteet, kaupat ja hinnat:")
                    st.markdown(response.choices[0].message.content)

    with col_c2:
        st.markdown("### 📋 Omat tallennetut hinnat & kaupat")
        edited_df = st.data_editor(st.session_state.custom_products, num_rows="dynamic", key="product_editor")
        
        if "Poista" in edited_df.columns:
            st.session_state.custom_products = edited_df[edited_df["Poista"] == False].reset_index(drop=True)
        else:
            st.session_state.custom_products = edited_df


# --- TAB 5: PERUSRUOKABUDJETOIJA ---
with tab5:
    st.subheader("4. Perusruokabudjetti & Kauppavinkit")
    family_size = st.selectbox("Talouden koko", ["1 henkilö", "2 henkilöä", "Perhe"])
    if st.button("Luo perusopas"):
        if not api_key:
            st.warning("Syötä sivupalkkiin OpenAI API-avain.")
        else:
            client = OpenAI(api_key=api_key)
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": f"Anna budjettivinkit ruokakauppaan taloudelle: {family_size}"}])
            st.markdown(resp.choices[0].message.content)


# --- TAB 6: RUOKALISTA & VERTAILU ---
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
            prompt = (
                f"Luo {days_count} päivän ruokalista noudattaen ruokavaliota '{diet_choice}', "
                f"kaloritavoitetta {daily_calories} kcal/päivä, ateriamäärää {meals_per_day} kpl/päivä, "
                f"ja tavoitetta '{goal_choice}'. Vältettävät allergiat/aineet: '{allergies_input}'. "
                f"Ota vertailuun mukaan kaupat: {', '.join(stores_to_compare)}."
            )
            resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
            st.markdown(resp.choices[0].message.content)
