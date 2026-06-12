import { Moon, Sun, Globe, Type } from "lucide-react";
import { useDarkMode } from "@/hooks/use-dark-mode";
import { useLanguage } from "@/hooks/use-language";
import { useFontSize } from "@/hooks/use-font-size";
import { Section, Row, Switch, SelectBox } from "./SettingsShared";

const General = () => {
  const [darkMode, setDarkMode] = useDarkMode();
  const [language, setLanguage] = useLanguage();
  const [fontSize, setFontSize] = useFontSize();
  const isUrdu = language === "ur";
  const s = (en, ur) => (isUrdu ? ur : en);

  return (
    <Section
      title={s("General", "عمومی")}
      desc={s("Appearance and language preferences.", "ظاہری شکل اور زبان کی ترجیحات۔")}
    >
      <Row
        icon={darkMode ? Moon : Sun}
        title={s("Dark mode", "ڈارک موڈ")}
        desc={s("Use a darker theme across the app.", "ایپلیکیشن میں گہرے رنگ کا تھیم استعمال کریں۔")}
      >
        <Switch checked={darkMode} onCheckedChange={setDarkMode} />
      </Row>

      <Row
        icon={Globe}
        title={s("Language", "زبان")}
        desc={s("Interface language.", "انٹرفیس زبان۔")}
      >
        <SelectBox
          value={language}
          onChange={setLanguage}
          options={[
            { value: "en", label: isUrdu ? "انگریزی" : "English" },
            { value: "ur", label: isUrdu ? "اردو" : "Urdu" },
          ]}
        />
      </Row>

      <Row
        icon={Type}
        title={s("Font size", "حرف کا سائز")}
        desc={s("Message text size.", "پیغام کے متن کا سائز۔")}
      >
        <SelectBox
          value={fontSize}
          onChange={setFontSize}
          options={[
            { value: "small", label: isUrdu ? "چھوٹا" : "Small" },
            { value: "medium", label: isUrdu ? "درمیانہ" : "Medium" },
            { value: "large", label: isUrdu ? "بڑا" : "Large" },
          ]}
        />
      </Row>
    </Section>
  );
};

export default General;
