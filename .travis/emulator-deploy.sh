docker login -u "$REGISTRY_USER" -p "$REGISTRY_PASS"

git_sha="$(git rev-parse --short HEAD)"

docker tag "$IMAGE_NAME" "${IMAGE_NAME}:develop"
docker tag "$IMAGE_NAME" "${IMAGE_NAME}:${git_sha}-develop"
docker push "${IMAGE_NAME}:develop" && docker push "${IMAGE_NAME}:${git_sha}-develop"
