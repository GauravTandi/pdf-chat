const pdfBox = document.getElementById("pdfBox")
const uploadBtn = document.getElementById("uploadBtn")

uploadBtn.addEventListener("click", async function () {
    const file = pdfBox.files[0]

    const formData = new FormData()

    formData.append("file", file)

    const response = await fetch(
        "https://super-space-system-r44ggx4ppp77cp954-8000.app.github.dev/upload",
        {
            method: "POST",
            body: formData
        }
    )

    const data = await response.json()
    
    console.log(data)
    console.log("Upload button clicked")

})

const askBtn = document.getElementById("askBtn");

askBtn.addEventListener("click", async () => {
    const question = document.getElementById("askBox").value;

    const response = await fetch(
        "https://super-space-system-r44ggx4ppp77cp954-8000.app.github.dev/ask",
        {
            method: "POST",
            headers:{
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                    question: question
            })
            
        }
    );

    const data  = await response.json();

    console.log(data);
    
    const aiAns = document.getElementById("aiAns");
    
    aiAns.innerText = data.answer; // why data.answer ? where we create this answer variable

});

