import React, { useState } from 'react';

function EditInfoPage() {
  const [name, setName] = useState('뿡순');
  const [number, setNumber] = useState('010-0000-0000');
  const [birth, setBirth] = useState('0000-00-00');

  const handleSave = () => {
    // Logic for saving updated info
    alert('Information saved!');
  };

  return (
    <div className="edit-info-container">
      <div className="edit-info-section">
        <h2>Edit Member Information</h2>
        <div className="edit-info-form">
          <div className="form-field">
            <label>Name:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label>전화번호</label>
            <input
              type="text"
              value={number}
              onChange={(e) => setNumber(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label>생년월일</label>
            <input
              type="text"
              value={birth}
              onChange={(e) => setBirth(e.target.value)}
            />
          </div>
          <button onClick={handleSave} className="save-button">
            Save
          </button>
        </div>
      </div>
    </div>
  );
}

export default EditInfoPage;
