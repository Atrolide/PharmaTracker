resource "aws_ecs_cluster" "ecs_cluster" {
  name = var.cluster_name
  tags = {
    Project = var.tag
  }
}

resource "aws_ecs_task_definition" "ecs_task" {
  family                   = var.task_family
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"

  execution_role_arn = var.execution_role_arn

  container_definitions = jsonencode([{
    name      = "${var.cluster_name}-container"
    image     = var.image
    memory    = 512
    cpu       = 256
    essential = true
    portMappings = [
      {
        containerPort = 80
        hostPort      = 80
      }
    ]
  }])

  tags = {
    Project = var.tag
  }
}

resource "aws_ecs_service" "ecs_service" {
  name            = "${var.cluster_name}-service"
  cluster         = aws_ecs_cluster.ecs_cluster.id
  task_definition = aws_ecs_task_definition.ecs_task.arn
  desired_count   = var.task_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = var.subnets
    security_groups  = var.security_groups
    assign_public_ip = true
  }
}
