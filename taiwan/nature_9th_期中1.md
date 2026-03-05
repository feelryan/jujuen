# 1. 學習目標 (Learning Objectives)

在完成這份教材的複習後，你應該具備以下能力：
After reviewing this material, you should possess the following abilities:

1.  **掌握電功率與電路安全**：能運用 $P=IV$ 與 $V=IR$ 計算燈泡亮度與電費，並理解保險絲與短路的原理。
    **Master Electric Power and Circuit Safety**: Be able to use $P=IV$ and $V=IR$ to calculate bulb brightness and electricity costs, and understand the principles of fuses and short circuits.

2.  **區分「電池」與「電解」**：能清楚分辨伏打電池（化學能轉電能）與電解（電能轉化學能）的電極定義與電子流向。
    **Distinguish between "Batteries" and "Electrolysis"**: Clearly differentiate between Voltaic cells (chemical to electrical energy) and electrolysis (electrical to chemical energy) regarding electrode definitions and electron flow.

3.  **判讀電流磁效應**：能熟練使用安培右手定則判斷導線周圍的磁場方向，以及螺線管的磁極。
    **Interpret the Magnetic Effect of Current**: Proficiently use the Right-Hand Grip Rule to determine the magnetic field direction around a wire and the magnetic poles of a solenoid.

4.  **分析天氣圖與氣象系統**：能看懂地面天氣圖，判斷高低氣壓的氣流方向（順/逆時針）及其對應的天氣型態（晴/雨）。
    **Analyze Weather Maps and Meteorological Systems**: Be able to read surface weather maps, determine airflow directions (clockwise/counter-clockwise) for high/low-pressure systems, and their corresponding weather patterns (sunny/rainy).

5.  **理解地質與板塊運動**：能分辨三大岩石（火成、沉積、變質）的成因，並理解板塊邊界（張裂、聚合）的地形特徵。
    **Understand Geology and Plate Tectonics**: Distinguish the origins of the three major rock types (igneous, sedimentary, metamorphic) and understand the topographic features of plate boundaries (divergent, convergent).

---

# 2. 單元與知識地圖 (Units & Knowledge Map)

根據試卷內容，本次考試範圍橫跨理化（電學、磁學、化學反應）與地科。
Based on the exam papers, the scope covers Physics/Chemistry (Electricity, Magnetism, Chemical Reactions) and Earth Science.

*   **單元 A：電與生活 (Electricity in Daily Life)**
    *   **核心：** 電功率 ($P$)、電流熱效應、家庭用電安全。
    *   **Core:** Electric Power ($P$), Heating effect of current, Household electrical safety.
    *   **直覺說明：** 探討電器「消耗能量的快慢」以及如何安全用電。
    *   **Intuitive explanation:** Explores "how fast appliances consume energy" and how to use electricity safely.

*   **單元 B：化學與電的轉換 (Conversion between Chemistry and Electricity)**
    *   **核心：** 伏打電池 (電池放電)、電解與電鍍 (消耗電能)。
    *   **Core:** Voltaic Cells (Battery discharging), Electrolysis and Electroplating (Consuming electrical energy).
    *   **直覺說明：** 電子在化學溶液中「誰丟誰撿」的遊戲。
    *   **Intuitive explanation:** A game of "who loses and who gains" electrons in chemical solutions.

*   **單元 C：電流磁效應 (Magnetic Effect of Current)**
    *   **核心：** 長直導線磁場、螺線管磁場、電動機。
    *   **Core:** Magnetic field of straight wires, Solenoid magnetic fields, Electric motors.
    *   **直覺說明：** 電流流過會產生磁場，讓指南針偏轉。
    *   **Intuitive explanation:** Electric current flowing creates a magnetic field that deflects a compass.

*   **單元 D：千變萬化的天氣與地質 (Changing Weather and Geology)**
    *   **核心：** 氣壓系統、鋒面、岩石循環、板塊構造。
    *   **Core:** Pressure systems, Fronts, Rock cycle, Plate tectonics.
    *   **直覺說明：** 天上空氣怎麼轉（決定天氣），地下石頭怎麼變（決定地形）。
    *   **Intuitive explanation:** How air turns in the sky (determining weather) and how rocks change underground (determining topography).

---

# 3. 關鍵觀念與必備公式 (Key Concepts & Formulas)

### 1. 電功率 (Electric Power)
*   **定義**：電器每秒鐘消耗的電能。亮度通常看功率大小。
    **Definition**: The electrical energy consumed by an appliance per second. Brightness usually depends on the power magnitude.
*   **公式 (Formulas)**：
    *   $P = I \times V$ （功率 = 電流 × 電壓，通用公式）
        $P = I \times V$ (Power = Current × Voltage, general formula)
    *   $P = I^2 \times R$ （串聯時好用，因為 $I$ 相同）
        $P = I^2 \times R$ (Useful for series circuits, since $I$ is constant)
    *   $P = \frac{V^2}{R}$ （並聯時好用，因為 $V$ 相同）
        $P = \frac{V^2}{R}$ (Useful for parallel circuits, since $V$ is constant)
*   **應用情境**：題目問「哪一顆燈泡比較亮」或「並聯後總功率變大還是變小」。
    **Context**: Questions asking "which bulb is brighter" or "does total power increase or decrease after parallel connection."

### 2. 伏打電池 vs. 電解 (Voltaic Cell vs. Electrolysis)
這是學生最容易搞混的觀念，請務必對照記憶。
This is the concept students most easily confuse; please memorize the contrast.

| 比較項目 (Item) | 伏打電池 (Voltaic Cell) | 電解/電鍍 (Electrolysis/Plating) |
| :--- | :--- | :--- |
| **能量轉換 (Energy)** | 化學能 $\to$ 電能 (主動供電) <br> Chemical $\to$ Electrical (Active source) | 電能 $\to$ 化學能 (被動耗電) <br> Electrical $\to$ Chemical (Passive load) |
| **負極 (-) (Negative)** | **活性大**的金屬，**失去**電子 (氧化) <br> **High activity** metal, **Loses** e- (Oxidation) | 接電源負極，**得到**電子 (還原) <br> Connects to source (-), **Gains** e- (Reduction) |
| **正極 (+) (Positive)** | **活性小**的金屬，**得到**電子 (還原) <br> **Low activity** metal, **Gains** e- (Reduction) | 接電源正極，**失去**電子 (氧化) <br> Connects to source (+), **Loses** e- (Oxidation) |
| **口訣 (Mnemonic)** | 負極溶解變輕 (通常) <br> Negative electrode dissolves/lightens (usually) | 負極變重 (金屬析出) <br> Negative electrode gets heavier (metal deposits) |

### 3. 北半球氣壓與氣流 (Pressure & Airflow in N. Hemisphere)
*   **高氣壓 (High Pressure, H)**：空氣**下沉**，地面氣流**順時鐘向外**旋出。天氣晴朗。
    **High Pressure (H)**: Air **sinks**, surface airflow spirals **clockwise and outward**. Weather is clear/sunny.
*   **低氣壓 (Low Pressure, L)**：空氣**上升**，地面氣流**逆時鐘向內**旋入。容易有雲雨。
    **Low Pressure (L)**: Air **rises**, surface airflow spirals **counter-clockwise and inward**. Prone to clouds and rain.
*   **直覺理解**：右手大拇指代表垂直氣流（高壓向下按，低壓向上比），四指彎曲代表旋轉方向。
    **Intuitive Understanding**: The right thumb represents vertical airflow (press down for High, point up for Low), and curled fingers represent rotation direction.

---

# 4. 典型題型整理 (Typical Question Patterns)

### 題型一：燈泡亮度比較 (Bulb Brightness Comparison)
*   **題型說明**：給定串聯或並聯電路，問哪顆燈泡最亮，或燈泡燒壞後其他燈泡亮度如何變化。
    **Description**: Given a series or parallel circuit, asks which bulb is brightest, or how brightness changes after one bulb burns out.
*   **解題步驟 (Steps)**：
    1.  **判斷串並聯**：串聯電流 ($I$) 相同，並聯電壓 ($V$) 相同。
        **Identify Series/Parallel**: Current ($I$) is the same in series; Voltage ($V$) is the same in parallel.
    2.  **選公式**：串聯比電阻 ($P=I^2R \Rightarrow R$ 大者亮)，並聯比電阻倒數 ($P=V^2/R \Rightarrow R$ 小者亮)。
        **Choose Formula**: In series, compare resistance ($P=I^2R \Rightarrow$ larger $R$ is brighter). In parallel, compare inverse resistance ($P=V^2/R \Rightarrow$ smaller $R$ is brighter).
    3.  **看變化**：若為並聯，其中一條支路斷掉，**不影響**其他支路的電壓與亮度（這是常考陷阱）。
        **Check Changes**: In parallel, if one branch breaks, it **does not affect** the voltage or brightness of other branches (this is a common trap).

### 題型二：電池與電解的質量變化 (Mass Change in Batteries/Electrolysis)
*   **題型說明**：給一張圖，問反應一段時間後，哪一根棒子變重？哪一杯顏色變淡？
    **Description**: Given a diagram, asks which rod gets heavier or which solution fades in color after some time.
*   **解題步驟 (Steps)**：
    1.  **找電源**：有電池符號的是「電解/電鍍」，沒有電池只有檢流計的是「伏打電池」。
        **Find Source**: If there's a battery symbol, it's "Electrolysis/Plating". If there's only a galvanometer, it's a "Voltaic Cell".
    2.  **定正負**：
        *   電池：活性大 = 負極 ($\to$ 溶解變輕)。
            Battery: High activity = Negative ($\to$ dissolves/lighter).
        *   電解：接負極 = 負極 ($\to$ 金屬析出變重)。
            Electrolysis: Connected to negative = Negative ($\to$ metal deposits/heavier).
    3.  **推論**：負極吸引正離子，正極吸引負離子。
        **Deduce**: Negative electrode attracts positive ions; Positive electrode attracts negative ions.

### 題型三：天氣圖判讀 (Weather Map Interpretation)
*   **題型說明**：給一張地面天氣圖，問某地點的風向或天氣狀況。
    **Description**: Given a surface weather map, asks for the wind direction or weather condition at a specific location.
*   **解題步驟 (Steps)**：
    1.  **找中心**：確認是高壓 (H) 還是低壓 (L)。
        **Find Center**: Confirm if it is High (H) or Low (L) pressure.
    2.  **畫切線**：不確定風向時，先畫出氣壓梯度力（由高壓指向低壓），再向右偏（北半球科氏力）。
        **Draw Tangent**: If unsure of wind direction, first draw the pressure gradient force (from High to Low), then deflect to the right (Coriolis force in N. Hemisphere).
    3.  **判斷天氣**：冷鋒過境後氣溫下降、氣壓上升；低壓中心附近多雨。
        **Judge Weather**: Temperature drops and pressure rises after a cold front passes; rainy near low-pressure centers.

---

# 5. 精選範例講解 (Worked Examples)

### 範例 1：電路功率分析 (Circuit Power Analysis)
**(改寫自中山國中試題 / Adapted from Zhongshan JH Exam)**
**題目**：甲、乙兩燈泡串聯時，甲比乙亮。若將兩燈泡改為並聯（電壓不變），則誰比較亮？
**Problem**: When bulbs A and B are connected in series, A is brighter than B. If they are reconnected in parallel (voltage remains constant), which one is brighter?

**解題思路 (Thought Process)**：
*   **直覺想法**：甲原本比較亮，是不是代表甲比較強？
    **Intuitive Idea**: A was originally brighter, does that mean A is "stronger"?
*   **修正觀念**：亮度看功率 ($P$)。
    **Correct Concept**: Brightness depends on Power ($P$).
    *   **Step 1 (串聯 Series)**：電流 $I$ 相同。$P = I^2 R$。甲亮 $\Rightarrow P_{A} > P_{B} \Rightarrow R_{A} > R_{B}$（甲電阻大）。
        **Step 1 (Series)**: Current $I$ is same. $P = I^2 R$. A is brighter $\Rightarrow P_{A} > P_{B} \Rightarrow R_{A} > R_{B}$ (A has higher resistance).
    *   **Step 2 (並聯 Parallel)**：電壓 $V$ 相同。$P = V^2 / R$。
        **Step 2 (Parallel)**: Voltage $V$ is same. $P = V^2 / R$.
    *   **Step 3 (比較 Compare)**：因為 $R_{A} > R_{B}$，分母越大功率越小。所以並聯時，電阻小的乙功率較大。
        **Step 3 (Compare)**: Since $R_{A} > R_{B}$, larger denominator means smaller power. So in parallel, B (smaller resistance) has higher power.
**答案**：乙燈泡較亮。
**Answer**: Bulb B is brighter.

### 範例 2：鋅銅電池原理 (Zinc-Copper Battery Principle)
**(改寫自新興國中試題 / Adapted from Xinxing JH Exam)**
**題目**：關於鋅銅電池放電過程，下列敘述何者正確？(A) 電子由銅片流向鋅片 (B) 鹽橋中的正離子移向銅片杯 (C) 鋅片質量增加。
**Problem**: Regarding the discharging process of a Zinc-Copper battery, which statement is correct? (A) Electrons flow from Copper to Zinc. (B) Positive ions in the salt bridge move to the Copper beaker. (C) The mass of the Zinc plate increases.

**解題思路 (Thought Process)**：
*   **Step 1 (活性 Activity)**：鋅 (Zn) > 銅 (Cu)。鋅當負極（氧化/溶解），銅當正極（還原/析出）。
    **Step 1 (Activity)**: Zinc (Zn) > Copper (Cu). Zinc is Negative (Oxidation/Dissolves), Copper is Positive (Reduction/Deposits).
*   **Step 2 (電子流 Electron Flow)**：電子由負極流向正極。Zn $\to$ Cu。所以 (A) 錯。
    **Step 2 (Electron Flow)**: Electrons flow from Negative to Positive. Zn $\to$ Cu. So (A) is wrong.
*   **Step 3 (離子流 Ion Flow)**：負極杯產生 $Zn^{2+}$ (正電太多)，需要鹽橋負離子過來中和；正極杯 $Cu^{2+}$ 變少 (正電不足)，需要鹽橋正離子過來補充。
    **Step 3 (Ion Flow)**: Negative beaker generates $Zn^{2+}$ (too much positive charge), needs negative ions from salt bridge; Positive beaker loses $Cu^{2+}$ (lacks positive charge), needs positive ions from salt bridge.
    *   口訣：正向正 (正離子流向正極杯)。
        Mnemonic: Positive to Positive (Positive ions flow to the positive beaker).
    *   所以 (B) 正確。
        So (B) is correct.
*   **Step 4 (質量 Mass)**：鋅片溶解變輕，銅片析出銅變重。所以 (C) 錯。
    **Step 4 (Mass)**: Zinc plate dissolves/lighter, Copper plate deposits copper/heavier. So (C) is wrong.
**答案**：(B)。
**Answer**: (B).

---

# 6. 常見錯誤與迷思 (Common Mistakes & Misconceptions)

1.  **混淆「電流」與「電子流」**
    **Confusing "Current" and "Electron Flow"**
    *   **錯誤 (Mistake)**：以為電流方向就是電子移動方向。
        Thinking current direction is the same as electron movement direction.
    *   **修正 (Correction)**：電流由正極流向負極；電子流由負極流向正極。兩者方向**相反**。
        Current flows from Positive to Negative; Electrons flow from Negative to Positive. They are **opposite**.
    *   **檢查方法 (Check)**：題目若問「金屬導線內」，移動的主角一定是「電子」。
        If the question asks about "inside a metal wire," the moving particle is always the "electron."

2.  **誤以為高氣壓天氣一定「熱」**
    **Mistakenly thinking High Pressure always means "Hot" weather**
    *   **錯誤 (Mistake)**：看到「高」氣壓就覺得溫度高。
        Seeing "High" pressure and assuming high temperature.
    *   **修正 (Correction)**：高氣壓代表空氣下沉，雲量少。夏天高壓確實熱（晴朗），但冬天大陸冷氣團也是高壓，卻是非常冷。重點是「晴朗穩定」，而非溫度高低。
        High pressure means sinking air and few clouds. Summer high pressure is hot (sunny), but winter continental cold air masses are also high pressure and very cold. The key is "clear and stable," not the temperature.

3.  **電鍍時，被鍍物接錯極**
    **Connecting the object to be plated to the wrong terminal during electroplating**
    *   **錯誤 (Mistake)**：想把鑰匙鍍上銅，卻把鑰匙接在正極。
        Wanting to plate copper onto a key but connecting the key to the positive terminal.
    *   **修正 (Correction)**：被鍍物品（鑰匙）要當「負極」，才能吸引正離子（銅離子）過來還原成金屬銅。
        The object to be plated (key) must be the "Negative" terminal to attract positive ions (copper ions) to reduce into copper metal.
    *   **口訣 (Mnemonic)**：**父**親**被**賭 (**負**極接**被**鍍物)。
        (Chinese mnemonic linking Negative to Plated object).

---

# 7. 建議練習與自我檢核 (Practice Suggestions & Self-Check)

### 練習建議 (Practice Suggestions)
1.  **先畫圖**：遇到電路題或受力題，不要只看文字，先把電路圖畫簡化，或畫出受力方向。
    **Draw first**: When facing circuit or force problems, don't just read the text; simplify the circuit diagram or draw force directions first.
2.  **比較題型**：找一題「伏打電池」和一題「電解水」的題目，並排在一起做，強迫自己寫出兩者的正負極定義差異。
    **Compare patterns**: Find one "Voltaic Cell" problem and one "Water Electrolysis" problem, do them side-by-side, and force yourself to write down the differences in electrode definitions.
3.  **地科圖像化**：看著天氣圖，用手比劃出風的流向，不要死背順時針/逆時針。
    **Visualize Earth Science**: Look at a weather map and use your hand to trace the wind flow; don't just memorize clockwise/counter-clockwise.

### 考前自我檢核表 (Pre-Exam Self-Checklist)

*   [ ] 我能寫出 $P=IV$ 與 $P=I^2R$ 的使用時機。
    I can state when to use $P=IV$ and $P=I^2R$.
*   [ ] 我能畫出鋅銅電池的裝置圖，並標示電子流向與鹽橋功能。
    I can draw a Zinc-Copper battery diagram and label the electron flow and salt bridge function.
*   [ ] 我能用右手定則判斷通電螺線管的 N 極在哪裡。
    I can use the right-hand rule to determine where the N-pole of a solenoid is.
*   [ ] 我能分辨冷鋒與暖鋒的符號，以及過境前後的氣溫變化。
    I can distinguish the symbols for cold and warm fronts and the temperature changes before and after they pass.
*   [ ] 我知道在北半球，低氣壓中心的空氣是上升還是下沉。
    I know whether the air in the center of a low-pressure system rises or sinks in the Northern Hemisphere.