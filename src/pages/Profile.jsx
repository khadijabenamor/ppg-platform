import { useEffect, useState } from "react";
import { getProfile, updateProfile , changePassword } from "../api/profile";

export default function Profile() {

  const token = localStorage.getItem("access_token");

  const [form, setForm] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
  });

  const [passwordData, setPasswordData] = useState({
    old_password: "",
    new_password: "",
    confirm_password: "",
  });
  const [message, setMessage] = useState("");

  const [avatar, setAvatar] = useState(null);
  const [avatarUrl, setAvatarUrl] = useState(null);
  {/*const [avatarUrl, setAvatarUrl] = useState("");*/}

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
      setAvatarUrl(res.data.avatar_url);
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
  const handlePasswordChange = (e) => {
  setPasswordData({
    ...passwordData,
    [e.target.name]: e.target.value,
  });
};
  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      {/*await updateProfile(token, form);*/}
      const formData = new FormData();

      formData.append("username", form.username);
      formData.append("first_name",form.first_name);
      formData.append("last_name",form.last_name);
      formData.append("email",form.email);
      if (avatar) {
          formData.append("avatar",avatar);
      }
      await updateProfile(token,formData);

      setMessage("Profil mis à jour avec succès");
    } catch (err) {
      setMessage("Erreur lors de la mise à jour");
    }
  };
  const handlePasswordSubmit = async (e) => {

  e.preventDefault();

  if (
    passwordData.new_password !==
    passwordData.confirm_password
  ) {
    setMessage(
      "Les mots de passe ne correspondent pas"
    );
    return;
  }

  try {

    const res =
      await changePassword(
        token,
        passwordData.old_password,
        passwordData.new_password
      );

    setMessage(
      res.data.message
    );

    setPasswordData({
      old_password: "",
      new_password: "",
      confirm_password: "",
    });

  } catch (err) {

    setMessage(
      err.response?.data?.error ||
      "Erreur"
    );

  }
};

  return (
    <div style={{
      maxWidth: "600px",
      margin: "40px auto",
      padding: "20px"
    }}>
    {avatarUrl && (
  <img
    src={avatarUrl}
    alt="avatar"
    style={{
      width: "120px",
      height: "120px",
      borderRadius: "50%",
      objectFit: "cover",
      display: "block",
      marginBottom: "20px"
    }}
  />
)}
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
        <div>
  <label>Photo de profil</label>

  <input
    type="file"
    accept="image/*"
    onChange={(e) =>
      setAvatar(
        e.target.files[0]
      )
    }
  />
</div>
          
        <button type="submit">
          Sauvegarder
        </button>

      </form>
      <hr />
      <h2>Changer le mot de passe</h2>
      <form onSubmit={handlePasswordSubmit}>

  <div>
    <label>Ancien mot de passe</label>
    <input
      type="password"
      name="old_password"
      value={passwordData.old_password}
      onChange={handlePasswordChange}
    />
  </div>

  <div>
    <label>Nouveau mot de passe</label>
    <input
      type="password"
      name="new_password"
      value={passwordData.new_password}
      onChange={handlePasswordChange}
    />
  </div>

  <div>
    <label>Confirmer le mot de passe</label>
    <input
      type="password"
      name="confirm_password"
      value={passwordData.confirm_password}
      onChange={handlePasswordChange}
    />
  </div>

  <button type="submit">
    Modifier le mot de passe
  </button>

</form>

      {message && (
        <p>{message}</p>
      )}

    </div>
  );
}