public class WeapData {
    private String range, attacks, balWeapSkill, damage;
    private int strength, armorPen;

    // WeapData.java
    @Override
    public String toString() {
        return String.format(
            "Range: %s\n" +
            "Attacks: %s\n" +
            "BS/WS: %s\n" +
            "Strength: %d\n" +
            "AP: %d\n" +
            "Damage: %s",
            range, attacks, balWeapSkill, strength, armorPen, damage
        );
    }


    public WeapData(String r, String a, String bws, int s, int ap, String d) {
        this.range        = r;
        this.attacks      = a;
        this.balWeapSkill = bws;
        this.strength     = s;
        this.armorPen     = ap;
        this.damage       = d;
    }

    public String getRange() {
        return range;
    }

    public String getAttacks() {
        return attacks;
    }

    public String getBalWeapSkill() {
        return balWeapSkill;
    }

    public int getStrength() {
        return strength;
    }

    public int getArmorPen() {
        return armorPen;
    }

    public String getDamage() {
        return damage;
    }

}