import { useEffect, useState } from "react";
import { getProfile, updateProfile } from "../api/profile";

export default function Profile() {

  const token = localStorage.getItem("access_token");

  const [form, setForm] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
  });

  const [message, setMessage] = useState("");

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await getProfile(token);

      setForm({
        username: res.data.username || "",
        first_name: res.data.first_name || "",
        last_name: res.data.last_name || "",
        email: res.data.email || "",
      });
    } catch (err) {
      console.error(err);
    }
  };

  const handleChange = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      await updateProfile(token, form);

      setMessage("Profil mis à jour avec succès");
    } catch (err) {
      setMessage("Erreur lors de la mise à jour");
    }
  };

  return (
    <div style={{
      maxWidth: "600px",
      margin: "40px auto",
      padding: "20px"
    }}>

      <h1>Mon Profil</h1>

      <form onSubmit={handleSubmit}>

        <div>
          <label>Nom d'utilisateur</label>
          <input
            name="username"
            value={form.username}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Prénom</label>
          <input
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Nom</label>
          <input
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
          />
        </div>

        <div>
          <label>Email</label>
          <input
            name="email"
            value={form.email}
            onChange={handleChange}
          />
        </div>

        <button type="submit">
          Sauvegarder
        </button>

      </form>

      {message && (
        <p>{message}</p>
      )}

    </div>
  );
}