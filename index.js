const express=require("express")

const app=express()

require("dotenv").config()

const PORT=process.env.PORT || 8000


const userRoutes=require("./routes/User")




const database=require("./config/dbConnect")
const cookieParser = require("cookie-parser")


const cors=require("cors")

database.connect()
app.use(express.json())
app.use(cookieParser())

app.use(

    cors({
        origin:"*",
        credentials:true,


    })
)


app.use("/api/v1/auth", userRoutes)

app.get("/", (req,res)=>{


    return res.json({

        success:true,
        message:"you are at the default home page of the system"
    })
})

app.listen(PORT, (req,res)=>{


    console.log(`App is running at ${PORT}`)
})